import requests
import json
import time
from datetime import datetime
from core.models import ApiCallStep, TaskHistoryRecord
from core.settings import get_settings
from core.logger import get_logger

class FedsfmApiClient:
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger()
        self.token = None
        self.base_url = self.settings.fedsfm_base_url
        self.prefix = "test-contur/" if self.settings.is_test_contur else ""

    def _make_url(self, endpoint: str) -> str:
        return f"{self.base_url}/{self.prefix}{endpoint}"

    def _create_step(self, stage: str, url: str, method: str, status_code: int, req_body: str, resp_body: str) -> ApiCallStep:
        return ApiCallStep(
            stage=stage,
            url=url,
            method=method,
            status_code=status_code,
            request_body=req_body,
            response_body=resp_body,
            timestamp=datetime.now().strftime(self.settings.log_time_format)
        )

    def execute_catalog_task(self, task_id: str, catalog_type: str, endpoint_catalog: str, endpoint_file: str, filename: str) -> TaskHistoryRecord:
        """Выполняет полную цепочку: Auth -> GetID -> Download"""
        history = TaskHistoryRecord(
            task_id=task_id,
            catalog_type=catalog_type,
            start_time=datetime.now().strftime(self.settings.log_time_format),
            end_time="",
            success=False
        )

        try:
            # ШАГ 1: Авторизация
            self.logger.log("INFO", f"[{catalog_type}] Начало авторизации...")
            auth_url = self._make_url("authenticate")
            req_body = json.dumps({"userName": self.settings.username, "password": self.settings.password})
            
            if self.settings.use_mock_api:
                time.sleep(0.5)
                self.token = "mock_jwt_token_12345"
                resp_body = '{"success": true, "value": {"accessToken": "mock_jwt_token_12345"}}'
                history.steps.append(self._create_step("Auth", auth_url, "POST", 200, req_body, resp_body))
            else:
                resp = requests.post(auth_url, json={"userName": self.settings.username, "password": self.settings.password}, verify=False, timeout=15)
                history.steps.append(self._create_step("Auth", auth_url, "POST", resp.status_code, req_body, resp.text[:500]))
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("success"):
                        self.token = data["value"]["accessToken"]
                    else:
                        raise Exception(f"Ошибка авторизации: {data.get('errors')}")

            # ШАГ 2: Получение ID каталога
            self.logger.log("INFO", f"[{catalog_type}] Запрос метаданных каталога...")
            cat_url = self._make_url(endpoint_catalog)
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            
            if self.settings.use_mock_api:
                time.sleep(0.5)
                mock_id = "mock-guid-xml-1234-5678"
                resp_body = f'{{"idXml": "{mock_id}", "isActive": true}}'
                history.steps.append(self._create_step("GetCatalogID", cat_url, "POST", 200, "{}", resp_body))
            else:
                resp = requests.post(cat_url, headers=headers, json={}, verify=False, timeout=15)
                history.steps.append(self._create_step("GetCatalogID", cat_url, "POST", resp.status_code, "{}", resp.text[:500]))
                resp.raise_for_status()
                data = resp.json()
                # Поддержка разных регистров из документации (idXml, IdXml, idTerroristCatalog)
                mock_id = data.get("idXml") or data.get("IdXml") or data.get("idTerroristCatalog")
                if not mock_id:
                    raise Exception("ID файла (idXml) не найден в ответе сервера")

            # ШАГ 3: Скачивание файла
            self.logger.log("INFO", f"[{catalog_type}] Скачивание файла (ID: {mock_id})...")
            file_url = self._make_url(endpoint_file)
            
            if self.settings.use_mock_api:
                time.sleep(1.0)
                resp_body = "Binary data (Mock 1024 bytes)"
                history.steps.append(self._create_step("DownloadFile", file_url, "POST", 200, f'{{"id": "{mock_id}"}}', resp_body))
            else:
                # Согласно доке: ContentType: application/x-www-form-urlencoded, параметр id
                resp = requests.post(file_url, headers=headers, data={"id": mock_id}, verify=False, stream=True, timeout=60)
                history.steps.append(self._create_step("DownloadFile", file_url, "POST", resp.status_code, f'{{"id": "{mock_id}"}}', f"Status: {resp.status_code}, Binary stream"))
                resp.raise_for_status()
                
                # Сохранение файла (в реальном режиме)
                import os
                os.makedirs(self.settings.download_dir, exist_ok=True)
                filepath = os.path.join(self.settings.download_dir, filename)
                with open(filepath, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.logger.log("INFO", f"[{catalog_type}] Файл сохранен: {filepath}")

            history.success = True
            self.logger.log("INFO", f"[{catalog_type}] Задача успешно завершена.")

        except Exception as e:
            history.error_message = str(e)
            self.logger.log("ERROR", f"[{catalog_type}] Ошибка выполнения: {str(e)}")
        
        finally:
            history.end_time = datetime.now().strftime(self.settings.log_time_format)
            
        return history