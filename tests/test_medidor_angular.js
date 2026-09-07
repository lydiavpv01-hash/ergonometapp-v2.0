/**
 * PRUEBAS UNITARIAS - Cálculo Angular
 * Valida que el cálculo geométrico sea matemáticamente correcto
 */

class AngularCalculatorTest {
    constructor() {
        this.results = [];
        this.passed = 0;
        this.failed = 0;
    }
    
    // Función de cálculo angular (duplicada de medidor_angular.js)
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
    
    // Prueba individual
    test(name, pointA, pointB, pointC, expectedAngle, tolerance = 0.1) {
        const result = this.calculateAngle(pointA, pointB, pointC);
        const passed = Math.abs(result - expectedAngle) < tolerance;
        
        this.results.push({
            name: name,
            expected: expectedAngle,
            result: result,
            passed: passed,
            error: Math.abs(result - expectedAngle)
        });
        
        if (passed) {
            this.passed++;
        } else {
            this.failed++;
        }
        
        return passed;
    }
    
    // Ejecutar todas las pruebas
    runAllTests() {
        console.log('=== PRUEBAS DE CÁLCULO ANGULAR ===\n');
        
        // PRUEBA 1: 0°
        this.test(
            'Ángulo 0° (puntos alineados)',
            { x: 0, y: 0 },     // A
            { x: 100, y: 0 },   // B (vértice)
            { x: 200, y: 0 },   // C
            0
        );
        
        // PRUEBA 2: 30°
        this.test(
            'Ángulo 30°',
            { x: 100, y: 0 },                          // A
            { x: 0, y: 0 },                            // B (vértice)
            { x: 100 * Math.cos(30 * Math.PI / 180), 
              y: 100 * Math.sin(30 * Math.PI / 180) }, // C
            30
        );
        
        // PRUEBA 3: 45°
        this.test(
            'Ángulo 45°',
            { x: 100, y: 0 },                          // A
            { x: 0, y: 0 },                            // B (vértice)
            { x: 100 * Math.cos(45 * Math.PI / 180), 
              y: 100 * Math.sin(45 * Math.PI / 180) }, // C
            45
        );
        
        // PRUEBA 4: 60°
        this.test(
            'Ángulo 60°',
            { x: 100, y: 0 },                          // A
            { x: 0, y: 0 },                            // B (vértice)
            { x: 100 * Math.cos(60 * Math.PI / 180), 
              y: 100 * Math.sin(60 * Math.PI / 180) }, // C
            60
        );
        
        // PRUEBA 5: 90° (perpendicular)
        this.test(
            'Ángulo 90° (perpendicular)',
            { x: 100, y: 0 },  // A (horizontal)
            { x: 0, y: 0 },    // B (vértice)
            { x: 0, y: 100 },  // C (vertical)
            90
        );
        
        // PRUEBA 6: 120°
        this.test(
            'Ángulo 120°',
            { x: 100, y: 0 },                            // A
            { x: 0, y: 0 },                              // B (vértice)
            { x: 100 * Math.cos(120 * Math.PI / 180), 
              y: 100 * Math.sin(120 * Math.PI / 180) },  // C
            120
        );
        
        // PRUEBA 7: 180° (línea recta)
        this.test(
            'Ángulo 180° (línea recta)',
            { x: 100, y: 0 },   // A
            { x: 0, y: 0 },     // B (vértice)
            { x: -100, y: 0 },  // C (opuesto a A)
            180
        );
        
        // PRUEBA 8: Invariancia a escala (mismo ángulo, coordenadas diferentes)
        this.test(
            'Invariancia a escala: 45° (x10)',
            { x: 1000, y: 0 },                         // A
            { x: 0, y: 0 },                            // B
            { x: 1000 * Math.cos(45 * Math.PI / 180), 
              y: 1000 * Math.sin(45 * Math.PI / 180) }, // C
            45
        );
        
        // PRUEBA 9: Invariancia a traslación
        const offsetX = 500;
        const offsetY = 300;
        this.test(
            'Invariancia a traslación: 45° (offset +500, +300)',
            { x: 100 + offsetX, y: 0 + offsetY },                          // A
            { x: 0 + offsetX, y: 0 + offsetY },                            // B
            { x: 100 * Math.cos(45 * Math.PI / 180) + offsetX, 
              y: 100 * Math.sin(45 * Math.PI / 180) + offsetY },           // C
            45
        );
        
        // PRUEBA 10: Ángulo obtuso (135°)
        this.test(
            'Ángulo obtuso 135°',
            { x: 100, y: 0 },                            // A
            { x: 0, y: 0 },                              // B (vértice)
            { x: 100 * Math.cos(135 * Math.PI / 180), 
              y: 100 * Math.sin(135 * Math.PI / 180) },  // C
            135
        );
    }
    
    // Imprimir resultados
    printResults() {
        console.log('\n=== RESULTADOS ===\n');
        
        this.results.forEach((r, i) => {
            const status = r.passed ? '✓ PASS' : '✗ FAIL';
            console.log(`${i + 1}. ${status} - ${r.name}`);
            console.log(`   Esperado: ${r.expected.toFixed(2)}°`);
            console.log(`   Obtenido: ${r.result.toFixed(2)}°`);
            console.log(`   Error: ${r.error.toFixed(4)}°\n`);
        });
        
        console.log(`\n=== RESUMEN ===`);
        console.log(`Pruebas pasadas: ${this.passed}/${this.results.length}`);
        console.log(`Pruebas fallidas: ${this.failed}/${this.results.length}`);
        console.log(`Tasa de éxito: ${((this.passed / this.results.length) * 100).toFixed(1)}%\n`);
        
        if (this.failed === 0) {
            console.log('✓ TODAS LAS PRUEBAS PASADAS\n');
        } else {
            console.log(`✗ ${this.failed} PRUEBAS FALLIDAS\n`);
        }
    }
    
    // Obtener resultados como JSON
    getResultsJSON() {
        return {
            timestamp: new Date().toISOString(),
            passed: this.passed,
            failed: this.failed,
            total: this.results.length,
            successRate: (this.passed / this.results.length * 100).toFixed(1),
            tests: this.results
        };
    }
}

// Ejecutar pruebas si se está en Node.js (para testing automático)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AngularCalculatorTest;
}

// O si se ejecuta en navegador
if (typeof window !== 'undefined') {
    window.AngularCalculatorTest = AngularCalculatorTest;
}
