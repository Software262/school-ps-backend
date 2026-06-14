import os
import re
import tempfile
import time
from pathlib import Path
from typing import Any

import pdfplumber
from playwright.sync_api import sync_playwright

from app.core.logger import setup_logger
from app.modules.webcolegios_import.domain.entities import (
    ScrapedStudent,
    ScrapedTeacher,
    WebcolegiosScrapeResult,
)
from app.modules.webcolegios_import.domain.service import normalize_grade_name

ELEMENT_TIMEOUT_MS = 15_000
DOWNLOAD_TIMEOUT_SECONDS = 45
DEFAULT_CHROMIUM_ARGS = ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]

logger = setup_logger()

GRADE_MAP = {
    "00": "Preescolar",
    "01": "Primero",
    "02": "Segundo",
    "03": "Tercero",
    "04": "Cuarto",
    "05": "Quinto",
    "06": "Sexto",
    "07": "Septimo",
    "08": "Octavo",
    "09": "Noveno",
    "10": "Decimo",
    "11": "Once",
    "JA": "Jardin",
    "PA": "Parvulos",
    "PJ": "Prejardin",
}

PERSON_PATTERN = re.compile(
    r"^\s*(\d+)\s+(\d{5,15})\s+([A-Z\u00c0-\u017f][A-Z\u00c0-\u017f\s]+?)"
    r"(?:\s+([A-Z0-9]{2})\s+([A-Z0-9]{2}))?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

TEACHER_PATTERN = re.compile(
    r"^\s*(?:(\d+)\s+)?(\d{5,15})\s+([A-Z\u00c0-\u017f][A-Z\u00c0-\u017f\s]+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


class WebcolegiosScraperAdapter:
    def run(self, url: str, usuario: str, contrasena: str) -> WebcolegiosScrapeResult:
        return self._run_with_browser(url, usuario, contrasena, "all")

    def run_students(
        self, url: str, usuario: str, contrasena: str
    ) -> WebcolegiosScrapeResult:
        return self._run_with_browser(url, usuario, contrasena, "students")

    def run_teachers(
        self, url: str, usuario: str, contrasena: str
    ) -> WebcolegiosScrapeResult:
        return self._run_with_browser(url, usuario, contrasena, "teachers")

    def _run_with_browser(
        self, url: str, usuario: str, contrasena: str, mode: str
    ) -> WebcolegiosScrapeResult:
        with tempfile.TemporaryDirectory(prefix="school_ps_webcolegios_") as temp_dir:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=self._get_headless(),
                    slow_mo=self._get_slow_mo(),
                    args=DEFAULT_CHROMIUM_ARGS,
                )
                context = None
                try:
                    context = browser.new_context(accept_downloads=True)
                    page = context.new_page()
                    students = []
                    teachers = []
                    if mode in ("all", "students"):
                        logger.info("Scrapeando estudiantes")
                        students = self._run_students(
                            context, page, url, usuario, contrasena, temp_dir
                        )
                    if mode in ("all", "teachers"):
                        context.clear_cookies()
                        logger.info("Scrapeando docentes")
                        teachers = self._run_teachers(
                            context, page, url, usuario, contrasena, temp_dir
                        )
                    return WebcolegiosScrapeResult(students=students, teachers=teachers)
                finally:
                    if context is not None:
                        context.close()
                    browser.close()

    def _get_headless(self) -> bool:
        return os.getenv("WEBCOLEGIOS_HEADLESS", "true").lower() != "false"

    def _get_slow_mo(self) -> int:
        value = os.getenv("WEBCOLEGIOS_SLOW_MO", "0")
        try:
            return max(int(value), 0)
        except ValueError:
            logger.warning("WEBCOLEGIOS_SLOW_MO invalido; usando 0")
            return 0

    def _run_students(self, context, page, url, usuario, contrasena, temp_dir: str):
        logger.info("Autenticando")
        self._authenticate(page, url, usuario, contrasena)
        logger.info("Login exitoso")
        result_page = self._navigate_student_listing(context, page, url, temp_dir)
        if result_page is None:
            raise RuntimeError("No se pudo obtener el listado de estudiantes.")
        return self._extract_students(result_page, temp_dir)

    def _run_teachers(self, context, page, url, usuario, contrasena, temp_dir: str):
        logger.info("Autenticando")
        self._authenticate(page, url, usuario, contrasena)
        logger.info("Login exitoso")
        result_page = self._navigate_student_listing(context, page, url, temp_dir)
        if result_page is None:
            raise RuntimeError("No se pudo obtener el listado de estudiantes.")

        holders = self._extract_holders_from_student_listing(result_page, temp_dir)
        if not holders:
            raise RuntimeError(
                "No se pudieron extraer titulares desde el listado de estudiantes."
            )

        teachers_raw = self._try_extract_teacher_personal_records(
            context,
            page,
            url,
            usuario,
            contrasena,
            temp_dir,
        )
        return self._build_teachers(teachers_raw, holders)

    def _authenticate(self, page, url: str, usuario: str, contrasena: str) -> None:
        page.goto(url)
        time.sleep(2)
        page.wait_for_selector(
            "//input[@id='identidad1' or @name='identidad1' or @type='text']",
            timeout=ELEMENT_TIMEOUT_MS,
        )
        page.locator(
            "//input[@id='identidad1' or @name='identidad1' or @type='text']"
        ).first.fill(usuario)
        page.wait_for_selector("//input[@type='password']", timeout=ELEMENT_TIMEOUT_MS)
        page.locator("//input[@type='password']").first.fill(contrasena)

        try:
            page.select_option(
                "//select[@id='nivel1' or @name='nivel1' or contains(@name,'tipo')]",
                label="Administrativo",
            )
        except Exception:
            pass

        captcha_text = self._get_captcha_text(page)
        answer = self._solve_math_captcha(captcha_text)
        page.wait_for_selector(
            "//input[@id='captcha_respuesta' or @name='captcha_respuesta' "
            "or contains(@name,'captcha') or contains(@id,'captcha')]",
            timeout=ELEMENT_TIMEOUT_MS,
        )
        page.locator(
            "//input[@id='captcha_respuesta' or @name='captcha_respuesta' "
            "or contains(@name,'captcha') or contains(@id,'captcha')]"
        ).first.fill(answer)
        page.locator(
            "//button[@id='boton'] | //input[@id='boton'] | "
            "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'acceder')] | "
            "//input[@type='submit']"
        ).first.click()
        self._accept_welcome_modal(page)
        if not self._verify_login_successful(page):
            raise RuntimeError("Login fallido en WebColegios.")

    def _get_captcha_text(self, page) -> str:
        selectors = [
            "//label[contains(text(),'=')]",
            "//td[contains(text(),'=')]",
            "//*[contains(@class,'captcha') or contains(@id,'captcha')]",
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                if locator.is_visible(timeout=1500):
                    text = locator.inner_text().strip()
                    if re.search(r"\d+\s*[\+\-\*\/]\s*\d+", text):
                        return text
            except Exception:
                continue

        match = re.search(r"\d+\s*[\+\-\*\/]\s*\d+", page.inner_text("body"))
        if not match:
            raise RuntimeError("No se pudo localizar el captcha matematico.")
        return match.group(0)

    def _solve_math_captcha(self, text: str) -> str:
        match = re.search(r"(\d+)\s*([\+\-\*\/])\s*(\d+)", text)
        if not match:
            raise RuntimeError("No se pudo interpretar el captcha matematico.")

        left = int(match.group(1))
        operator = match.group(2)
        right = int(match.group(3))
        result = {
            "+": left + right,
            "-": left - right,
            "*": left * right,
            "/": left // right,
        }[operator]
        return str(result)

    def _accept_welcome_modal(self, page) -> None:
        end = time.time() + 20
        while time.time() < end:
            try:
                button = page.locator(
                    "//input[@type='submit' and @value='Acceder']"
                ).first
                if button.is_visible(timeout=500) and button.is_enabled():
                    button.click()
                    break
            except Exception:
                pass
            time.sleep(0.5)
        time.sleep(2)

    def _verify_login_successful(self, page) -> bool:
        url_actual = page.url.lower()
        if "login" not in url_actual:
            return True

        indicators = [
            "//div[contains(@class,'menu')]",
            "//nav",
            "//a[contains(text(),'Cerrar') or contains(text(),'Salir')]",
            "//span[contains(text(),'Bienvenido') or contains(text(),'bienvenido')]",
        ]
        for selector in indicators:
            try:
                if page.locator(selector).first.is_visible(timeout=1000):
                    return True
            except Exception:
                continue

        errors = [
            "//span[contains(text(),'incorrecto') or contains(text(),'invalido')]",
            "//div[contains(@class,'error') or contains(@class,'alert-danger')]",
        ]
        for selector in errors:
            try:
                if page.locator(selector).first.is_visible(timeout=1000):
                    return False
            except Exception:
                continue

        return True

    def _go_to_listing_form(self, page, url: str) -> None:
        base = url.rstrip("/")
        if "/" in base.split("//")[-1]:
            base = base.rsplit("/", 1)[0]
        form_url = f"{base}/admin_lista_uso_general.php"
        page.goto(form_url)
        time.sleep(2)
        if self._is_listing_form_valid(page):
            return

        logger.warning(
            "Acceso directo al listado bloqueado; intentando navegacion por menu"
        )
        page.goto(url)
        self._accept_welcome_modal(page)
        time.sleep(1)
        self._click_by_text(page, "administrativo", tag="a")
        time.sleep(1)
        self._click_by_text(page, "listas")
        time.sleep(1)
        if not self._click_by_text(page, "uso general", tag="a"):
            self._click_by_text(page, "uso general")
        time.sleep(2)

        if not self._is_listing_form_valid(page):
            raise RuntimeError(
                "No se pudo abrir admin_lista_uso_general.php desde WebColegios."
            )

    def _is_listing_form_valid(self, page) -> bool:
        try:
            page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass

        if "admin_lista_uso_general" not in page.url:
            return False

        try:
            if page.locator("text='Acceso Denegado'").count() > 0:
                return False
            return (
                page.locator("input[type='radio']").count() > 0
                or page.locator("select").count() > 0
            )
        except Exception:
            return False

    def _click_by_text(self, page, text: str, tag: str = "*") -> bool:
        text_lower = text.lower()
        xpath = (
            f"//{tag}[contains("
            "translate(normalize-space(text()),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZÃÃ‰ÃÃ“ÃšÃ‘',"
            "'abcdefghijklmnopqrstuvwxyzÃ¡Ã©Ã­Ã³ÃºÃ±'),"
            f"'{text_lower}')]"
        )
        try:
            locator = page.locator(xpath).first
            if locator.is_visible(timeout=2000):
                locator.click()
                return True
        except Exception:
            pass

        for frame in page.frames:
            try:
                locator = frame.locator(xpath).first
                if locator.is_visible(timeout=1000):
                    locator.click()
                    return True
            except Exception:
                continue
        return False

    def _select_data_type(self, page, tipo: str) -> None:
        tipo_lower = tipo.lower()
        strategies = [
            f"//label[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÑ','abcdefghijklmnopqrstuvwxyzáéíóúñ'),'{tipo_lower}')]//input[@type='radio']",
            f"//input[@type='radio' and following-sibling::text()[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÑ','abcdefghijklmnopqrstuvwxyzáéíóúñ'),'{tipo_lower}')]]",
        ]
        for selector in strategies:
            try:
                radio = page.locator(selector).first
                radio.wait_for(state="attached", timeout=3000)
                radio.check()
                return
            except Exception:
                continue

        for index in range(page.locator("select").count()):
            select = page.locator("select").nth(index)
            if select.locator(f"option:has-text('{tipo}')").count() > 0:
                select.select_option(label=tipo)
                return

    def _mark_not_retired(self, page) -> None:
        selectors = [
            "//label[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÑ','abcdefghijklmnopqrstuvwxyzáéíóúñ'),'retirados')]",
            "//input[@id='soloretirados']/preceding::input[@type='checkbox'][1]",
        ]
        for selector in selectors:
            try:
                element = page.locator(selector).first
                element.wait_for(state="attached", timeout=3000)
                if element.evaluate("node => node.tagName.toLowerCase()") == "label":
                    for_attr = element.get_attribute("for")
                    checkbox = (
                        page.locator(f"id={for_attr}")
                        if for_attr
                        else element.locator("input").first
                    )
                else:
                    checkbox = element
                if not checkbox.is_checked():
                    checkbox.check()
                return
            except Exception:
                continue

    def _click_next(self, page) -> None:
        page.click(
            "//button[@id='button'] | //input[@id='button'] | "
            "//input[contains(translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'siguiente')] | "
            "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'siguiente')]"
        )
        time.sleep(2)

    def _uncheck_single_site_listing(self, page) -> None:
        try:
            checkbox = page.locator("id=escuela_nueva")
            if checkbox.count() and checkbox.is_checked():
                checkbox.uncheck()
        except Exception:
            pass

    def _navigate_student_listing(self, context, page, url: str, temp_dir: str):
        pdf_path = Path(temp_dir) / "impresion.pdf"

        def handle_route(route):
            response = route.fetch()
            content_type = response.headers.get("content-type", "").lower()
            if "application/pdf" in content_type:
                pdf_path.write_bytes(response.body())
            route.fulfill(response=response)

        self._go_to_listing_form(page, url)
        self._select_data_type(page, "Estudiantes")
        self._mark_not_retired(page)
        self._click_next(page)
        self._uncheck_single_site_listing(page)

        context.route("**/*", handle_route)
        try:
            with context.expect_page(timeout=15_000) as new_page_info:
                page.click(
                    "//input[contains(translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'imprimir') "
                    "or contains(@class,'btn-dark')] | "
                    "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'imprimir')]"
                )
            result_page = new_page_info.value
            result_page.wait_for_load_state(timeout=5000)
            return result_page
        except Exception:
            pages = context.pages
            return pages[-1] if len(pages) > 1 else None
        finally:
            try:
                context.unroute("**/*", handle_route)
            except Exception:
                pass

    def _download_teacher_holder_pdfs(self, page, url: str, temp_dir: str) -> list[str]:
        self._go_to_listing_form(page, url)
        self._mark_not_retired(page)
        self._click_next(page)
        return self._download_visible_pdfs(page, temp_dir, "titulares_grado")

    def _download_teacher_listing(self, page, url: str, temp_dir: str) -> str | None:
        self._go_to_listing_form(page, url)
        self._select_data_type(page, "Docentes")
        self._click_next(page)
        target = Path(temp_dir) / "docentes_listado.pdf"

        selectors = [
            "//input[contains(translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'imprimir todos')] | "
            "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'imprimir todos')]",
            "input[type='image'][src*='print_p']",
        ]
        for selector in selectors:
            try:
                button = page.locator(selector).first
                button.wait_for(state="visible", timeout=5000)
                with page.expect_download(timeout=20_000) as download_info:
                    button.click()
                download_info.value.save_as(str(target))
                return str(target)
            except Exception:
                continue
        return None

    def _download_visible_pdfs(self, page, temp_dir: str, prefix: str) -> list[str]:
        selectors = [
            "input[type='image'][src*='print_p']",
            "img[src*='print_p']",
            "a:has(img[src*='pdf'])",
            "a[href*='pdf']",
            "a:has-text('PDF')",
            "img[alt*='pdf' i]",
        ]
        elements = []
        for selector in selectors:
            try:
                locator = page.locator(selector)
                for index in range(locator.count()):
                    element = locator.nth(index)
                    if element.is_visible(timeout=500):
                        elements.append(element)
            except Exception:
                continue

        paths = []
        for index, element in enumerate(elements):
            try:
                with page.expect_download(timeout=10_000) as download_info:
                    element.click(timeout=3000)
                path = Path(temp_dir) / f"{prefix}_{index}.pdf"
                download_info.value.save_as(str(path))
                paths.append(str(path))
            except Exception:
                continue
        return paths

    def _extract_students(self, page, temp_dir: str) -> list[ScrapedStudent]:
        records = self._extract_from_html(page, "estudiantes")
        if not records:
            pdf = self._wait_for_pdf(temp_dir)
            records = self._extract_from_pdf(pdf, "estudiantes") if pdf else []

        return [
            ScrapedStudent(
                nombre=record.get("nombre", ""),
                documento=record.get("documento", ""),
                grado_nombre=record.get("grado_nombre") or record.get("grado_texto"),
                curso=record.get("curso"),
                sede=record.get("sede"),
                jornada=record.get("jornada"),
                titular_nombre=record.get("titular"),
                acudiente_nombre=record.get("acudiente_nombre"),
                acudiente_telefono=record.get("acudiente_telefono"),
                acudiente_correo=record.get("acudiente_correo"),
                raw_data=record,
            )
            for record in records
        ]

    def _build_teachers(
        self, records: list[dict[str, Any]], holders: list[dict[str, str]]
    ) -> list[ScrapedTeacher]:
        teachers_by_name = {
            self._normalize_name(record.get("nombre", "")): record
            for record in records
            if self._normalize_name(record.get("nombre", ""))
        }

        teachers = []
        for holder in holders:
            holder_name = holder.get("titular_nombre", "")
            personal_record = teachers_by_name.get(self._normalize_name(holder_name))
            document = personal_record.get("documento", "") if personal_record else ""
            subject = (
                personal_record.get("asignatura")
                if personal_record
                else "SIN ASIGNATURA"
            )
            teachers.append(
                ScrapedTeacher(
                    nombre=holder_name,
                    documento=document,
                    asignatura=subject or "SIN ASIGNATURA",
                    grado_titular=holder.get("grado_nombre"),
                    curso_titular=holder.get("curso"),
                    sede=holder.get("sede"),
                    jornada=holder.get("jornada"),
                    raw_data={
                        "titular": holder,
                        "docente": personal_record or {},
                        "documento_resuelto": bool(document),
                    },
                )
            )
        return teachers

    def _try_extract_teacher_personal_records(
        self, context, page, url: str, usuario: str, contrasena: str, temp_dir: str
    ) -> list[dict[str, Any]]:
        try:
            context.clear_cookies()
            logger.info("Autenticando para cruce opcional de Personal DOCENTE")
            self._authenticate(page, url, usuario, contrasena)
            logger.info("Login exitoso")
            teacher_pdf = self._download_teacher_listing(page, url, temp_dir)
            if teacher_pdf is None:
                logger.warning(
                    "No se pudo descargar Personal DOCENTE; "
                    "los titulares sin documento quedaran pendientes"
                )
                return []
            return self._extract_from_pdf(teacher_pdf, "docentes")
        except Exception as exc:
            logger.warning(
                "No se pudo obtener Personal DOCENTE; "
                "los titulares sin documento quedaran pendientes: {}",
                exc,
            )
            return []

    def _extract_holders_from_student_listing(
        self, page, temp_dir: str
    ) -> list[dict[str, str]]:
        records = []
        listing_text = self._extract_listing_text(page)
        records.extend(self._extract_holders_from_student_text(listing_text))

        pdf = self._latest_student_pdf(temp_dir)
        if pdf is None and not records:
            pdf = self._wait_for_pdf(temp_dir)

        if pdf:
            for page_text in self._read_pdf_pages(pdf):
                records.extend(self._extract_holders_from_student_text(page_text))

        return self._dedupe_holder_records(records)

    def _extract_listing_text(self, page) -> str:
        text = ""
        try:
            tables = page.locator("//table")
            for index in range(tables.count()):
                text += tables.nth(index).inner_text() + "\n"
            if not text.strip():
                text = page.inner_text("body")
        except Exception:
            return ""
        return text

    def _latest_student_pdf(self, temp_dir: str) -> str | None:
        pdfs = [
            path
            for path in Path(temp_dir).glob("*.pdf")
            if "titulares" not in path.name
        ]
        if not pdfs:
            return None
        return str(max(pdfs, key=os.path.getmtime))

    def _extract_holders_from_student_text(self, text: str) -> list[dict[str, str]]:
        if not text:
            return []

        pattern = re.compile(
            r"Jornada\s*:\s*(?P<jornada>.*?)\s+"
            r"Grado\s*:\s*(?P<grado>.*?)\s+"
            r"Curso\s*:\s*(?P<curso>.*?)\s+"
            r"Sede\s*:\s*(?P<sede>.*?)\s+"
            r"Titular\s*:\s*(?P<titular>.*?)(?=\s+Fecha\s*:|\s+Jornada\s*:|$)",
            re.IGNORECASE | re.DOTALL,
        )

        return [
            {
                "jornada": self._clean_header_value(match.group("jornada")),
                "grado_nombre": normalize_grade_name(match.group("grado")),
                "curso": self._clean_header_value(match.group("curso")),
                "sede": self._clean_header_value(match.group("sede")),
                "titular_nombre": self._clean_name(match.group("titular")),
            }
            for match in pattern.finditer(text)
            if self._clean_name(match.group("titular"))
        ]

    def _dedupe_holder_records(
        self, records: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        holders = {}
        for record in records:
            name = self._clean_name(record.get("titular_nombre", ""))
            key = self._normalize_name(name)
            if not key:
                continue

            holders[key] = {
                **record,
                "titular_nombre": name,
            }
        return list(holders.values())

    def _clean_header_value(self, value: str | None) -> str:
        cleaned = re.sub(r"\s+", " ", value or "").strip()
        return re.sub(r"\s*:\s*$", "", cleaned)

    def _extract_from_html(self, page, tipo: str) -> list[dict[str, Any]]:
        text = ""
        try:
            tables = page.locator("//table")
            for index in range(tables.count()):
                text += tables.nth(index).inner_text() + "\n"
            if not text.strip():
                text = page.inner_text("body")
        except Exception:
            return []
        return self._parse_text(text, tipo)

    def _extract_from_pdf(
        self, pdf_path: str | None, tipo: str
    ) -> list[dict[str, Any]]:
        if not pdf_path or not os.path.exists(pdf_path):
            return []
        try:
            import pdfplumber
        except ImportError as exc:
            raise RuntimeError("pdfplumber no esta instalado.") from exc

        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return self._parse_text("\n".join(pages), tipo)

    def _extract_holders_from_pdfs(self, paths: list[str]) -> dict[str, dict[str, str]]:
        holders = {}
        for path in paths:
            text = "\n".join(
                page_text for page_text in self._read_pdf_pages(path) if page_text
            )
            name = self._match_value(
                r"Titular\s*:\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,}?)(?=\s+Fecha:|$)", text
            )
            grade = self._match_value(
                r"Grado\s*:\s*([A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s]+?)(?=\s+Curso:|$)", text
            )
            course = self._match_value(r"Curso\s*:\s*([A-Za-z0-9]+)", text)
            if name:
                holders[self._clean_name(name)] = {
                    "grado_titular": grade.strip().capitalize() if grade else "",
                    "curso_titular": self._map_course(course or ""),
                }
        return holders

    def _read_pdf_pages(self, path: str) -> list[str]:

        with pdfplumber.open(path) as pdf:
            return [page.extract_text() or "" for page in pdf.pages]

    def _wait_for_pdf(self, temp_dir: str) -> str | None:
        end = time.time() + DOWNLOAD_TIMEOUT_SECONDS
        while time.time() < end:
            pdfs = [
                str(path)
                for path in Path(temp_dir).glob("*.pdf")
                if "titulares" not in path.name
            ]
            if pdfs:
                return max(pdfs, key=os.path.getmtime)
            time.sleep(1)
        return None

    def _parse_text(self, text: str, tipo: str) -> list[dict[str, Any]]:
        if not text:
            return []

        jornada = self._extract_header(text, r"Jornada:\s*([^\n\r]+?)(?=\s+Grado:|$)")
        grade = self._extract_header(text, r"Grado:\s*([^\n\r]+?)(?=\s+Curso:|$)")
        course = self._extract_header(text, r"Curso:\s*([^\n\r]+?)(?=\s+Sede:|$)")
        sede = self._extract_header(text, r"Sede:\s*([^\n\r]+)")
        titular = self._extract_header(text, r"Titular:\s*([^\n\r]+?)(?=\s+Fecha:|$)")

        if not jornada and "Jornada:" in sede:
            jornada_match = re.search(
                r"Jornada:\s*([a-zA-Z0-9_]+)", sede, re.IGNORECASE
            )
            if jornada_match:
                jornada = jornada_match.group(1).strip()
            sede = re.sub(
                r"\s*Jornada:\s*[a-zA-Z0-9_]+", "", sede, flags=re.IGNORECASE
            ).strip()

        if tipo == "docentes":
            return [
                {
                    "consecutivo": int(match[0] or 0),
                    "documento": match[1].strip(),
                    "nombre": self._clean_name(match[2]),
                    "jornada": jornada,
                    "grado_nombre": grade,
                    "curso": course,
                    "sede": sede,
                    "titular": titular,
                }
                for match in TEACHER_PATTERN.findall(text)
                if self._clean_name(match[2]) and match[1].strip()
            ]

        return [
            {
                "consecutivo": int(consecutive),
                "documento": document.strip(),
                "nombre": self._clean_name(name),
                "jornada": jornada,
                "grado_nombre": GRADE_MAP.get(grade_code, grade_code)
                if grade_code
                else grade,
                "curso": self._map_course(course_code)
                if course_code
                else self._map_course(course),
                "sede": sede,
                "titular": titular,
            }
            for consecutive, document, name, grade_code, course_code in PERSON_PATTERN.findall(
                text
            )
            if self._clean_name(name) and document.strip()
        ]

    def _extract_header(self, text: str, pattern: str) -> str:
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _match_value(self, pattern: str, text: str) -> str | None:
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _clean_name(self, name: str) -> str:
        cleaned = re.sub(r"\s+", " ", name).strip()
        cleaned = re.sub(r"[^A-Za-z\u00c0-\u017f\s]", "", cleaned).strip()
        return cleaned[:150]

    def _normalize_name(self, name: str) -> str:
        return re.sub(r"\s+", "", self._clean_name(name)).lower()

    def _map_course(self, code: str) -> str:
        try:
            number = int(code)
            if 1 <= number <= 26:
                return chr(ord("A") + number - 1)
        except ValueError:
            pass
        return code.strip().upper() if code else ""
