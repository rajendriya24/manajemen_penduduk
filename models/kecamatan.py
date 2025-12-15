# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Kecamatan(models.Model):
    _name = 'penduduk.kecamatan'
    _description = 'Master Kecamatan'
    _order = 'kabupaten_id, name'
    _rec_name = 'name'

    name = fields.Char(string='Nama Kecamatan', required=True, index=True)
    kode = fields.Char(string='Kode Kecamatan', index=True)

    # ❗ dibuat TIDAK required agar import tidak gagal sebelum create()
    kabupaten_id = fields.Many2one(
        'penduduk.kabupaten',
        string='Kabupaten/Kota',
        required=False,
        ondelete='restrict',
        index=True,
        domain="[('active','=',True)]",
    )

    # provinsi otomatis ikut dari kabupaten (CSV tidak perlu provinsi)
    provinsi_id = fields.Many2one(
        'penduduk.provinsi',
        string='Provinsi',
        related='kabupaten_id.provinsi_id',
        store=True,
        readonly=True,
        index=True,
    )

    # field bantu import (map dari CSV)
    kabupaten_code = fields.Char(
        string='Kode Kabupaten (Import)',
        index=True,
        help="Isi dengan kode kabupaten, contoh 11.01. Saat import, sistem akan set Kabupaten/Kota otomatis."
    )

    active = fields.Boolean(string='Aktif', default=True)

    _sql_constraints = [
        ('kecamatan_kode_unique', 'unique(kode)', 'Kode Kecamatan harus unik!'),
        ('kecamatan_name_kab_unique', 'unique(name, kabupaten_id)', 'Nama Kecamatan pada kabupaten/kota yang sama harus unik!'),
    ]

    # ---------- VALIDASI KODE (boleh titik) ----------
    @api.constrains('kode')
    def _check_kode(self):
        for rec in self:
            if not rec.kode:
                continue
            kode = (rec.kode or '').strip()
            allowed_chars = set("0123456789.")
            if not set(kode).issubset(allowed_chars):
                raise ValidationError(_("Kode Kecamatan hanya boleh berisi angka dan titik (contoh: 11.01.01)."))
            if kode.startswith('.') or kode.endswith('.'):
                raise ValidationError(_("Kode Kecamatan tidak boleh diawali atau diakhiri titik."))
            if '..' in kode:
                raise ValidationError(_("Kode Kecamatan tidak boleh mengandung dua titik berturut-turut."))

    # ---------- WAJIBKAN kabupaten_id (setelah create/write) ----------
    @api.constrains('kabupaten_id')
    def _check_kabupaten_required(self):
        for rec in self:
            if not rec.kabupaten_id:
                raise ValidationError(_("Kabupaten/Kota wajib diisi."))

    # ---------- AUTO SET kabupaten_id DARI kabupaten_code ----------
    def _apply_kabupaten_code(self, vals):
        # kalau user/import sudah isi kabupaten_id, skip
        if vals.get('kabupaten_id'):
            return vals

        code = (vals.get('kabupaten_code') or '').strip()
        if not code:
            return vals

        kab = self.env['penduduk.kabupaten'].sudo().search([('kode', '=', code)], limit=1)
        if not kab:
            raise ValidationError(
                _("Kabupaten dengan kode '%s' tidak ditemukan. Pastikan Kabupaten sudah ter-import.") % code
            )

        vals['kabupaten_id'] = kab.id
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        new_vals_list = []
        for vals in vals_list:
            vals = dict(vals)
            vals = self._apply_kabupaten_code(vals)
            new_vals_list.append(vals)
        return super().create(new_vals_list)

    def write(self, vals):
        vals = dict(vals)
        vals = self._apply_kabupaten_code(vals)
        return super().write(vals)

    def name_get(self):
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