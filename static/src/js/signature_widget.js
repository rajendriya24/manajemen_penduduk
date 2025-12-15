/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUpdateProps, useRef } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

class SignaturePadField extends Component {
    setup() {
        this.canvasRef = useRef("canvas");
        this.ctx = null;
        this.isDrawing = false;

        const initCanvas = () => {
            const canvas = this.canvasRef.el;
            if (!canvas) return;

            canvas.width = 420;
            canvas.height = 160;

            this.ctx = canvas.getContext("2d");
            this.ctx.lineWidth = 2;
            this.ctx.lineCap = "round";
            this.ctx.strokeStyle = "#111";
        };

        const drawFromValue = (val) => {
            const canvas = this.canvasRef.el;
            if (!canvas || !this.ctx) return;

            this.ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (!val) return;
            const img = new Image();
            img.onload = () => {
                this.ctx.clearRect(0, 0, canvas.width, canvas.height);
                this.ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            };
            img.src = `data:image/png;base64,${val}`;
        };

        const getPos = (ev) => {
            const canvas = this.canvasRef.el;
            const rect = canvas.getBoundingClientRect();
            const clientX = ev.touches ? ev.touches[0].clientX : ev.clientX;
            const clientY = ev.touches ? ev.touches[0].clientY : ev.clientY;
            return { x: clientX - rect.left, y: clientY - rect.top };
        };

        const start = (ev) => {
            ev.preventDefault();
            if (!this.ctx) return;
            this.isDrawing = true;
            const p = getPos(ev);
            this.ctx.beginPath();
            this.ctx.moveTo(p.x, p.y);
        };

        const move = (ev) => {
            if (!this.isDrawing || !this.ctx) return;
            ev.preventDefault();
            const p = getPos(ev);
            this.ctx.lineTo(p.x, p.y);
            this.ctx.stroke();
        };

        const end = (ev) => {
            if (!this.isDrawing || !this.ctx) return;
            ev.preventDefault();
            this.isDrawing = false;

            const canvas = this.canvasRef.el;
            const dataUrl = canvas.toDataURL("image/png");
            const base64 = dataUrl.split(",")[1];

            // ✅ simpan ke field (langsung ke record)
            this.props.record.update({ [this.props.name]: base64 });
        };

        onMounted(() => {
            initCanvas();

            const val = this.props.record.data[this.props.name];
            drawFromValue(val);

            const canvas = this.canvasRef.el;
            canvas.addEventListener("mousedown", start);
            canvas.addEventListener("mousemove", move);
            window.addEventListener("mouseup", end);

            canvas.addEventListener("touchstart", start, { passive: false });
            canvas.addEventListener("touchmove", move, { passive: false });
            window.addEventListener("touchend", end, { passive: false });
        });

        onWillUpdateProps((nextProps) => {
            if (!this.ctx) return;
            const currentVal = this.props.record.data[this.props.name];
            const nextVal = nextProps.record.data[nextProps.name];
            if (currentVal !== nextVal) {
                drawFromValue(nextVal);
            }
        });

        this._drawFromValue = drawFromValue;
    }

    clearSignature() {
        const canvas = this.canvasRef.el;
        if (!canvas || !this.ctx) return;
        this.ctx.clearRect(0, 0, canvas.width, canvas.height);
        this.props.record.update({ [this.props.name]: false });
    }
}

SignaturePadField.template = "penduduk_management.SignaturePadField";
SignaturePadField.props = { ...standardFieldProps };

registry.category("fields").add("signature_pad", {
    component: SignaturePadField,
});