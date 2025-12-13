# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Kelurahan(models.Model):
    _name = 'penduduk.kelurahan'
    _description = 'Master Kelurahan/Desa'
    _order = 'provinsi_id, kabupaten_id, kecamatan_id, name'
    _rec_name = 'name'

    name = fields.Char(string='Nama Kelurahan/Desa', required=True, index=True)
    kode = fields.Char(string='Kode Kelurahan/Desa', index=True)

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
    kecamatan_id = fields.Many2one(
        'penduduk.kecamatan',
        string='Kecamatan',
        required=True,
        ondelete='restrict',
        index=True,
        domain="[('kabupaten_id','=',kabupaten_id), ('active','=',True)]",
    )

    active = fields.Boolean(string='Aktif', default=True)

    _sql_constraints = [
        ('kelurahan_kode_unique', 'unique(kode)', 'Kode Kelurahan/Desa harus unik!'),
        ('kelurahan_name_kec_unique', 'unique(name, kecamatan_id)', 'Nama Kelurahan/Desa pada kecamatan yang sama harus unik!'),
    ]

    @api.constrains('kode')
    def _check_kode(self):
        for rec in self:
            if not rec.kode:
                continue
            kode = (rec.kode or '').strip()
            if not kode.isdigit():
                raise ValidationError(_("Kode Kelurahan/Desa harus berupa angka."))
            if len(kode) < 2 or len(kode) > 10:
                raise ValidationError(_("Panjang Kode Kelurahan/Desa harus 2 sampai 10 digit."))

    @api.onchange('provinsi_id')
    def _onchange_provinsi_id(self):
        """
        Jika provinsi diganti, turunan harus dikosongkan bila mismatch.
        """
        if self.kabupaten_id and self.kabupaten_id.provinsi_id != self.provinsi_id:
            self.kabupaten_id = False
        self.kecamatan_id = False

    @api.onchange('kabupaten_id')
    def _onchange_kabupaten_id(self):
        """
        Jika kabupaten diganti, kecamatan dikosongkan bila mismatch.
        """
        if self.kecamatan_id and self.kecamatan_id.kabupaten_id != self.kabupaten_id:
            self.kecamatan_id = False

    def name_get(self):
        """
        Dropdown enak:
        Kelurahan X [kode] - Kecamatan
        """
        res = []
        for rec in self:
            label = rec.name
            if rec.kode:
                label = f"{label} [{rec.kode}]"
            if rec.kecamatan_id:
                label = f"{label} - {rec.kecamatan_id.name}"
            res.append((rec.id, label))
        return res

    def toggle_active(self):
        for rec in self:
            rec.active = not rec.active