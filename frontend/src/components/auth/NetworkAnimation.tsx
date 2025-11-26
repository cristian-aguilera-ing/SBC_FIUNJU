import React, { useEffect, useRef } from 'react';

export const NetworkAnimation: React.FC = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    // Usamos refs para guardar la posición del mouse sin provocar re-renders
    const mouseRef = useRef({ x: -1000, y: -1000 });
    
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let width = 0;
        let height = 0;
        let animationId: number;

        // Configuración de nodos
        const nodeCount = 110; // Un poco menos de nodos para que no se sature al ser más grandes
        const connectionDistance = 110; // Aumenté la distancia de conexión para que se unan más
        const mouseInteractionRadius = 80;
        const repulsionRadius = 60; 

        interface Node {
            x: number;
            y: number;
            vx: number;
            vy: number;
            radius: number;
            baseVx: number;
            baseVy: number;
        }

        const nodes: Node[] = [];

        const initNodes = () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
            nodes.length = 0; // Limpiar array

            for (let i = 0; i < nodeCount; i++) {
                // Aumenté la velocidad base (antes * 1.0)
                const vx = (Math.random() - 0.5) * 1.5; 
                const vy = (Math.random() - 0.5) * 1.5;
                nodes.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    vx: vx,
                    vy: vy,
                    baseVx: vx,
                    baseVy: vy,
                    // Nodos más grandes (antes * 2 + 1.5)
                    radius: Math.random() * 2.5 + 2 
                });
            }
        };

        // Inicializar
        initNodes();

        const handleMouseMove = (e: MouseEvent) => {
            mouseRef.current = { x: e.clientX, y: e.clientY };
        };
        
        const handleResize = () => {
            initNodes();
        };

        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('resize', handleResize);

        const animate = () => {
            ctx.clearRect(0, 0, width, height);
            
            const mouseX = mouseRef.current.x;
            const mouseY = mouseRef.current.y;

            // Encontrar nodo más cercano al mouse
            let closestNodeIndex = -1;
            let minDistanceToMouse = mouseInteractionRadius;

            for (let i = 0; i < nodes.length; i++) {
                const node = nodes[i];
                const dx = mouseX - node.x;
                const dy = mouseY - node.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < minDistanceToMouse) {
                    minDistanceToMouse = dist;
                    closestNodeIndex = i;
                }
            }

            // Dibujar y actualizar nodos
            for (let i = 0; i < nodes.length; i++) {
                const node = nodes[i];
                const isTargetNode = (i === closestNodeIndex);

                // --- Atracción del Mouse ---
                if (isTargetNode) {
                    const dx = mouseX - node.x;
                    const dy = mouseY - node.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist > 0) {
                        const force = (mouseInteractionRadius - dist) / mouseInteractionRadius;
                        const attractionStrength = 0.08; // Un poco más fuerte
                        node.vx += dx * force * attractionStrength;
                        node.vy += dy * force * attractionStrength;
                    }
                } else {
                    // Retorno a velocidad base (inercia)
                    node.vx += (node.baseVx - node.vx) * 0.05;
                    node.vy += (node.baseVy - node.vy) * 0.05;
                }

                // --- Repulsión entre nodos ---
                for (let j = 0; j < nodes.length; j++) {
                    if (i === j) continue;
                    const other = nodes[j];
                    const dx = node.x - other.x;
                    const dy = node.y - other.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < repulsionRadius && dist > 0) {
                        const force = (repulsionRadius - dist) / repulsionRadius;
                        const repulsionStrength = 0.03; 

                        const nx = dx / dist;
                        const ny = dy / dist;

                        node.vx += nx * force * repulsionStrength;
                        node.vy += ny * force * repulsionStrength;
                    }
                }

                // Limitar velocidad máxima (aumentada de 3.0 a 5.0)
                const speed = Math.sqrt(node.vx * node.vx + node.vy * node.vy);
                const maxSpeed = 5.0;
                if (speed > maxSpeed) {
                    node.vx = (node.vx / speed) * maxSpeed;
                    node.vy = (node.vy / speed) * maxSpeed;
                }

                // Mover
                node.x += node.vx;
                node.y += node.vy;

                // Rebote en bordes
                if (node.x < 0 || node.x > width) {
                    node.x = Math.max(0, Math.min(width, node.x));
                    node.vx *= -1; node.baseVx *= -1;
                }
                if (node.y < 0 || node.y > height) {
                    node.y = Math.max(0, Math.min(height, node.y));
                    node.vy *= -1; node.baseVy *= -1;
                }

                // Dibujar Nodo
                ctx.beginPath();
                ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
                
                if (isTargetNode) {
                    ctx.fillStyle = '#a855f7'; // Violeta brillante
                    ctx.shadowBlur = 20;
                    ctx.shadowColor = '#a855f7';
                } else {
                    ctx.fillStyle = '#06b6d4'; // Cian
                    ctx.shadowBlur = 5; // Un poco de brillo a todos los nodos
                    ctx.shadowColor = '#06b6d4';
                }
                ctx.fill();
                ctx.shadowBlur = 0;

                // Dibujar Conexiones
                for (let j = i + 1; j < nodes.length; j++) {
                    const other = nodes[j];
                    const dx = other.x - node.x;
                    const dy = other.y - node.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < connectionDistance) {
                        ctx.beginPath();
                        ctx.moveTo(node.x, node.y);
                        ctx.lineTo(other.x, other.y);
                        
                        const alpha = 1 - (dist / connectionDistance);
                        // Líneas más visibles: aumenté alpha base de 0.4 a 0.6 y width a 1.5
                        ctx.strokeStyle = `rgba(6, 182, 212, ${alpha * 0.6})`; 
                        ctx.lineWidth = 1.5; 
                        ctx.stroke();
                    }
                }

                // Conexión al mouse
                if (isTargetNode) {
                     const dx = mouseX - node.x;
                     const dy = mouseY - node.y;
                     const dist = Math.sqrt(dx * dx + dy * dy);
                     if (dist < mouseInteractionRadius) {
                        ctx.beginPath();
                        ctx.moveTo(node.x, node.y);
                        ctx.lineTo(mouseX, mouseY);
                        const alpha = 1 - (dist / mouseInteractionRadius);
                        ctx.strokeStyle = `rgba(168, 85, 247, ${alpha})`; 
                        ctx.lineWidth = 2.5; 
                        ctx.stroke();
                     }
                }
            } 

            animationId = requestAnimationFrame(animate);
        };

        animate();
        
        return () => {
            window.removeEventListener('resize', handleResize);
            window.removeEventListener('mousemove', handleMouseMove);
            cancelAnimationFrame(animationId);
        };
    }, []);

    return (
        <div className="absolute inset-0 pointer-events-none z-10 overflow-hidden">
            <canvas ref={canvasRef} className="absolute inset-0 w-full h-full opacity-80 mix-blend-screen" />
        </div>
    );
};