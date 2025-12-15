{
    "name": "Manajemen Penduduk",
    "version": "1.0",
    "category": "Tools",
    "author": "Rajen",
    "depends": ["base", "web"],

    "data": [
        "security/ir.model.access.csv",
        "views/provinsi_views.xml",
        "views/kabupaten_views.xml",
        "views/kecamatan_views.xml",
        "views/kelurahan_views.xml",
        "views/penduduk_views.xml",
        "report/ktp_report.xml",
        "report/ktp_template.xml",
    ],

    "assets": {
        "web.assets_backend": [
            "penduduk_management/static/src/js/signature_widget.js",
            "penduduk_management/static/src/xml/signature_widget.xml",
            "penduduk_management/static/src/scss/penduduk.scss",
        ],
    },

    "installable": True,
    "application": True,
}