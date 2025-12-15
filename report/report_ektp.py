from odoo import api, models


class ReportEKTP(models.AbstractModel):
    _name = "report.penduduk_management.report_ektp_template"
    _description = "Report e-KTP Penduduk"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["penduduk.penduduk"].browse(docids)
        print("### EKTP REPORT DOCIDS:", docids)
        print("### EKTP REPORT DOCS:", docs)
        return {
            "doc_ids": docids,
            "doc_model": "penduduk.penduduk",
            "docs": docs,
        }