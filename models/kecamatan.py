# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Kecamatan(models.Model):
    _name = 'penduduk.kecamatan'
    _description = 'Master Kecamatan'
    _order = 'provinsi_id, kabupaten_id, name'
    _rec_name = 'name'

    name = fields.Char(string='Nama Kecamatan', required=True, index=True)
    kode = fields.Char(string='Kode Kecamatan', index=True)

    provinsi_id = fields.Many2one(
        'penduduk.provinsi',
        string='Provinsi',
        required=True,
        ondelete='restrict',
        index=True,
    )
    kabupaten_id = fields.Many2one(
        'penduduk.kabupaten',
        string='Kabupaten/Kota',
        required=True,
        ondelete='restrict',
        index=True,
        domain="[('provinsi_id','=',provinsi_id), ('active','=',True)]",
    )

    active = fields.Boolean(string='Aktif', default=True)

    _sql_constraints = [
        ('kecamatan_kode_unique', 'unique(kode)', 'Kode Kecamatan harus unik!'),
        ('kecamatan_name_kab_unique', 'unique(name, kabupaten_id)', 'Nama Kecamatan pada kabupaten/kota yang sama harus unik!'),
    ]

    @api.constrains('kode')
    def _check_kode(self):
        for rec in self:
            if not rec.kode:
                continue
            kode = (rec.kode or '').strip()
            if not kode.isdigit():
                raise ValidationError(_("Kode Kecamatan harus berupa angka."))
            if len(kode) < 2 or len(kode) > 10:
                raise ValidationError(_("Panjang Kode Kecamatan harus 2 sampai 10 digit."))

    @api.onchange('provinsi_id')
    def _onchange_provinsi_id(self):
        """
        Jika provinsi diganti, kabupaten dikosongkan supaya tidak mismatch.
        """
        if self.kabupaten_id and self.kabupaten_id.provinsi_id != self.provinsi_id:
            self.kabupaten_id = False

    def name_get(self):
        """
        Dropdown enak: Kecamatan X [kode] - Kabupaten
        """
        res = []
        for rec in self:
            label = rec.name
            if rec.kode:
                label = f"{label} [{rec.kode}]"
            if rec.kabupaten_id:
                label = f"{label} - {rec.kabupaten_id.name}"
            res.append((rec.id, label))
        return res

    def toggle_active(self):
        for rec in self:
            rec.active = not rec.active