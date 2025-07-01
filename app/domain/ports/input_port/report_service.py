# app/domain/ports/input_port/report_service.py

from abc import ABC, abstractmethod
from typing import BinaryIO

from app.infrastructure.dto.reports_schema import WordReportDTO

class IWordReportUseCase(ABC):
    """
    Interfaz para generar diferentes tipos de reportes.
    """

    @abstractmethod
    def generate_monthly_report(self, dto: WordReportDTO) -> BinaryIO:
        """Genera el reporte mensual en formato Word."""
        pass

    @abstractmethod
    def generate_incidents_report(self, dto: WordReportDTO) -> BinaryIO:
        """Genera el reporte de incidentes en formato Word."""
        pass

    @abstractmethod
    def generate_saso_excel_report(self, dto: WordReportDTO) -> BinaryIO:
        """Genera reporte SASO en Excel."""
        pass

    @abstractmethod
    def generate_single_case_report(self, case_number: str, dto: WordReportDTO) -> BinaryIO:
        """Genera un reporte único para un caso (incidente, SR o cambio) en formato Word."""
        pass
