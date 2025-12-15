from odoo import models, api
import base64

class ReportEktp(models.AbstractModel):
    _name = 'report.penduduk_management.report_ektp_template'
    _description = 'Report e-KTP'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['penduduk.penduduk'].browse(docids)

        def to_data_uri(img):
            if not img:
                return False
            # fields.Image biasanya base64 string; tapi amankan kalau bytes
            if isinstance(img, bytes):
                b64 = base64.b64encode(img).decode()
            else:
                b64 = img
            return 'data:image/png;base64,%s' % b64

        return {
            'doc_ids': docs.ids,
            'doc_model': 'penduduk.penduduk',
            'docs': docs,
            'to_data_uri': to_data_uri,  # INI YANG BIKIN TEMPLATE TIDAK ERROR
        }