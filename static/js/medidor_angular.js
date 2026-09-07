/**
 * MEDIDOR ANGULAR INTERACTIVO
 * Herramienta para medición de ángulos sobre fotografías
 * 
 * Cálculo geométrico invariante a zoom y pan
 */

class MedidorAngular {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        // Estado de la imagen
        this.image = null;
        this.imageWidth = 0;
        this.imageHeight = 0;
        
        // Estado de visualización (zoom y pan)
        this.zoom = 1;
        this.panX = 0;
        this.panY = 0;
        
        // Puntos de medición (en coordenadas de imagen)
        this.points = [];
        this.activePointIndex = null;
        this.isDragging = false;
        
        // Mediciones guardadas
        this.measurements = [];
        this.currentMeasurement = null;
        
        // Configuración
        this.pointRadius = 8;
        this.lineWidth = 2;
        this.colors = {
            pointA: '#FF6B6B',
            pointB: '#4ECDC4',
            pointC: '#95E1D3',
            line: '#667eea',
            arc: 'rgba(102, 126, 234, 0.3)',
            arcStroke: '#667eea'
        };
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        this.canvas.addEventListener('mouseleave', (e) => this.handleMouseLeave(e));
        this.canvas.addEventListener('wheel', (e) => this.handleZoom(e));
    }
    
    // ==================== CARGA DE IMAGEN ====================
    loadImage(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                const img = new Image();
                img.onload = () => {
                    this.image = img;
                    this.imageWidth = img.width;
                    this.imageHeight = img.height;
                    
                    // Resetear mediciones al cargar nueva imagen
                    this.points = [];
                    this.measurements = [];
                    this.currentMeasurement = null;
                    this.zoom = 1;
                    this.panX = 0;
                    this.panY = 0;
                    
                    this.fitImageToCanvas();
                    this.draw();
                    
                    resolve({
                        width: img.width,
                        height: img.height,
                        size: `${img.width}x${img.height}px`
                    });
                };
                
                img.onerror = () => reject(new Error('Error al cargar la imagen'));
                img.src = e.target.result;
            };
            
            reader.onerror = () => reject(new Error('Error al leer el archivo'));
            reader.readAsDataURL(file);
        });
    }
    
    fitImageToCanvas() {
        if (!this.image) return;
        
        const canvasAspect = this.canvas.width / this.canvas.height;
        const imageAspect = this.imageWidth / this.imageHeight;
        
        if (imageAspect > canvasAspect) {
            this.zoom = this.canvas.width / this.imageWidth;
        } else {
            this.zoom = this.canvas.height / this.imageHeight;
        }
        
        this.centerImage();
    }
    
    centerImage() {
        const scaledWidth = this.imageWidth * this.zoom;
        const scaledHeight = this.imageHeight * this.zoom;
        
        this.panX = (this.canvas.width - scaledWidth) / 2;
        this.panY = (this.canvas.height - scaledHeight) / 2;
    }
    
    // ==================== CONVERSIÓN DE COORDENADAS ====================
    /**
     * Convierte coordenadas de pantalla (canvas) a coordenadas de imagen
     * Invariante a zoom y pan
     */
    screenToImage(screenX, screenY) {
        const imageX = (screenX - this.panX) / this.zoom;
        const imageY = (screenY - this.panY) / this.zoom;
        return { x: imageX, y: imageY };
    }
    
    /**
     * Convierte coordenadas de imagen a pantalla (canvas)
     */
    imageToScreen(imageX, imageY) {
        const screenX = imageX * this.zoom + this.panX;
        const screenY = imageY * this.zoom + this.panY;
        return { x: screenX, y: screenY };
    }
    
    // ==================== CÁLCULO GEOMÉTRICO ====================
    /**
     * Calcula el ángulo entre tres puntos
     * Utiliza geometría vectorial
     * El ángulo se calcula en el vértice B
     */
    calculateAngle(pointA, pointB, pointC) {
        // Vector 1: B -> A
        const v1x = pointA.x - pointB.x;
        const v1y = pointA.y - pointB.y;
        
        // Vector 2: B -> C
        const v2x = pointC.x - pointB.x;
        const v2y = pointC.y - pointB.y;
        
        // Producto punto
        const dotProduct = v1x * v2x + v1y * v2y;
        
        // Magnitudes
        const mag1 = Math.sqrt(v1x * v1x + v1y * v1y);
        const mag2 = Math.sqrt(v2x * v2x + v2y * v2y);
        
        // Evitar división por cero
        if (mag1 === 0 || mag2 === 0) return 0;
        
        // Coseno del ángulo
        const cosAngle = dotProduct / (mag1 * mag2);
        
        // Limitar a [-1, 1] por errores de punto flotante
        const clampedCos = Math.max(-1, Math.min(1, cosAngle));
        
        // Ángulo en radianes
        const angleRad = Math.acos(clampedCos);
        
        // Ángulo en grados
        const angleDeg = angleRad * (180 / Math.PI);
        
        return angleDeg;
    }
    
    // ==================== MANEJO DE EVENTOS ====================
    handleCanvasClick(e) {
        if (!this.image) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const screenX = e.clientX - rect.left;
        const screenY = e.clientY - rect.top;
        
        // Convertir a coordenadas de imagen
        const { x: imageX, y: imageY } = this.screenToImage(screenX, screenY);
        
        // Verificar si se hace click en un punto existente
        const clickedPointIndex = this.getPointAtLocation(imageX, imageY);
        
        if (clickedPointIndex !== null) {
            this.activePointIndex = clickedPointIndex;
            this.isDragging = true;
            return;
        }
        
        // Agregar nuevo punto si no hay 3 aún
        if (this.points.length < 3) {
            this.points.push({ x: imageX, y: imageY, label: String.fromCharCode(65 + this.points.length) });
            
            // Si hay 3 puntos, crear medición
            if (this.points.length === 3) {
                this.createMeasurement();
            }
        }
        
        this.draw();
    }
    
    handleMouseMove(e) {
        if (!this.image || this.activePointIndex === null || !this.isDragging) {
            this.updateCursor(e);
            return;
        }
        
        const rect = this.canvas.getBoundingClientRect();
        const screenX = e.clientX - rect.left;
        const screenY = e.clientY - rect.top;
        
        const { x: imageX, y: imageY } = this.screenToImage(screenX, screenY);
        
        // Actualizar posición del punto
        this.points[this.activePointIndex].x = imageX;
        this.points[this.activePointIndex].y = imageY;
        
        // Recalcular medición si hay 3 puntos
        if (this.points.length === 3) {
            this.currentMeasurement = this.calculateMeasurement();
        }
        
        this.draw();
    }
    
    handleMouseUp(e) {
        this.isDragging = false;
        this.activePointIndex = null;
    }
    
    handleMouseLeave(e) {
        this.isDragging = false;
    }
    
    handleZoom(e) {
        if (!this.image) return;
        
        e.preventDefault();
        
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        const zoomSpeed = 1.1;
        const oldZoom = this.zoom;
        
        // Cambiar zoom
        if (e.deltaY < 0) {
            this.zoom *= zoomSpeed;
        } else {
            this.zoom /= zoomSpeed;
        }
        
        // Limitar zoom
        this.zoom = Math.max(0.5, Math.min(3, this.zoom));
        
        // Ajustar pan para mantener el cursor en el mismo lugar
        const zoomRatio = this.zoom / oldZoom;
        this.panX = mouseX - (mouseX - this.panX) * zoomRatio;
        this.panY = mouseY - (mouseY - this.panY) * zoomRatio;
        
        this.draw();
    }
    
    updateCursor(e) {
        if (!this.image) {
            this.canvas.style.cursor = 'default';
            return;
        }
        
        const rect = this.canvas.getBoundingClientRect();
        const screenX = e.clientX - rect.left;
        const screenY = e.clientY - rect.top;
        
        const { x: imageX, y: imageY } = this.screenToImage(screenX, screenY);
        
        if (this.getPointAtLocation(imageX, imageY) !== null) {
            this.canvas.style.cursor = 'grab';
        } else if (this.points.length < 3) {
            this.canvas.style.cursor = 'crosshair';
        } else {
            this.canvas.style.cursor = 'default';
        }
    }
    
    // ==================== UTILIDADES ====================
    getPointAtLocation(x, y, tolerance = 10) {
        for (let i = 0; i < this.points.length; i++) {
            const point = this.points[i];
            const distance = Math.sqrt((x - point.x) ** 2 + (y - point.y) ** 2);
            if (distance < tolerance) {
                return i;
            }
        }
        return null;
    }
    
    createMeasurement() {
        if (this.points.length !== 3) return null;
        
        return this.calculateMeasurement();
    }
    
    calculateMeasurement() {
        const angle = this.calculateAngle(this.points[0], this.points[1], this.points[2]);
        
        return {
            id: Date.now(),
            points: JSON.parse(JSON.stringify(this.points)),
            angle: angle,
            timestamp: new Date().toLocaleTimeString()
        };
    }
    
    // ==================== DIBUJO ====================
    draw() {
        // Limpiar canvas
        this.ctx.fillStyle = '#fafafa';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Dibujar imagen
        if (this.image) {
            this.ctx.save();
            this.ctx.translate(this.panX, this.panY);
            this.ctx.scale(this.zoom, this.zoom);
            this.ctx.drawImage(this.image, 0, 0);
            this.ctx.restore();
        }
        
        // Dibujar puntos
        this.drawPoints();
        
        // Dibujar medición si hay 3 puntos
        if (this.points.length === 3 && this.currentMeasurement) {
            this.drawMeasurement();
        }
    }
    
    drawPoints() {
        const colors = [this.colors.pointA, this.colors.pointB, this.colors.pointC];
        
        for (let i = 0; i < this.points.length; i++) {
            const point = this.points[i];
            const { x: screenX, y: screenY } = this.imageToScreen(point.x, point.y);
            
            // Dibujar punto
            this.ctx.fillStyle = colors[i];
            this.ctx.beginPath();
            this.ctx.arc(screenX, screenY, this.pointRadius, 0, 2 * Math.PI);
            this.ctx.fill();
            
            // Borde del punto
            this.ctx.strokeStyle = 'white';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            // Etiqueta
            this.ctx.fillStyle = '#333';
            this.ctx.font = 'bold 12px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(point.label, screenX, screenY);
        }
    }
    
    drawMeasurement() {
        const p1 = this.imageToScreen(this.points[0].x, this.points[0].y);
        const p2 = this.imageToScreen(this.points[1].x, this.points[1].y);
        const p3 = this.imageToScreen(this.points[2].x, this.points[2].y);
        
        // Dibujar líneas
        this.ctx.strokeStyle = this.colors.line;
        this.ctx.lineWidth = this.lineWidth;
        
        this.ctx.beginPath();
        this.ctx.moveTo(p1.x, p1.y);
        this.ctx.lineTo(p2.x, p2.y);
        this.ctx.lineTo(p3.x, p3.y);
        this.ctx.stroke();
        
        // Dibujar arco
        this.drawAngleArc(p1, p2, p3);
        
        // Mostrar valor del ángulo
        this.drawAngleValue(p2);
    }
    
    drawAngleArc(p1, p2, p3) {
        // Vectores
        const v1x = p1.x - p2.x;
        const v1y = p1.y - p2.y;
        const v2x = p3.x - p2.x;
        const v2y = p3.y - p2.y;
        
        // Ángulos de los vectores
        const angle1 = Math.atan2(v1y, v1x);
        const angle2 = Math.atan2(v2y, v2x);
        
        // Radio del arco
        const radius = 40;
        
        // Dibujar arco
        this.ctx.fillStyle = this.colors.arc;
        this.ctx.strokeStyle = this.colors.arcStroke;
        this.ctx.lineWidth = 2;
        
        this.ctx.beginPath();
        this.ctx.arc(p2.x, p2.y, radius, angle1, angle2, angle2 < angle1);
        this.ctx.lineTo(p2.x, p2.y);
        this.ctx.fill();
        this.ctx.stroke();
    }
    
    drawAngleValue(p2) {
        if (!this.currentMeasurement) return;
        
        const angle = this.currentMeasurement.angle.toFixed(1);
        const text = `${angle}°`;
        
        // Offset para evitar sobreposición
        const offsetX = 60;
        const offsetY = -20;
        
        // Fondo del texto
        this.ctx.fillStyle = 'rgba(102, 126, 234, 0.9)';
        this.ctx.font = 'bold 16px Arial';
        this.ctx.textAlign = 'center';
        
        const metrics = this.ctx.measureText(text);
        const textWidth = metrics.width;
        const textHeight = 20;
        
        this.ctx.fillRect(
            p2.x + offsetX - textWidth / 2 - 5,
            p2.y + offsetY - textHeight / 2,
            textWidth + 10,
            textHeight
        );
        
        // Texto
        this.ctx.fillStyle = 'white';
        this.ctx.fillText(text, p2.x + offsetX, p2.y + offsetY + 3);
    }
    
    // ==================== GESTIÓN DE MEDICIONES ====================
    saveMeasurement() {
        if (this.currentMeasurement) {
            this.measurements.push(this.currentMeasurement);
            return this.currentMeasurement;
        }
        return null;
    }
    
    deleteMeasurement(id) {
        this.measurements = this.measurements.filter(m => m.id !== id);
    }
    
    clearCurrentPoints() {
        this.points = [];
        this.currentMeasurement = null;
        this.draw();
    }
    
    repeatMeasurement() {
        this.clearCurrentPoints();
    }
    
    getState() {
        return {
            imageWidth: this.imageWidth,
            imageHeight: this.imageHeight,
            zoom: this.zoom,
            panX: this.panX,
            panY: this.panY,
            measurements: this.measurements,
            currentPoints: this.points,
            currentMeasurement: this.currentMeasurement
        };
    }
}

// Exportar para uso en HTML
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MedidorAngular;
}
