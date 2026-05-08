"""Vagalumes animados que fluem pelas salas.

Demonstra uso de:
- desenhar_circulo: corpo do vagalume
- floodfill: brilho interno
- Animação 2D com movimento sinusoidal e pulsação
"""

import math
from render.primitivas import desenhar_circulo, flood_fill

class Vagalume:
    """Vagalume animado com movimento fluido e pulsação."""
    
    def __init__(self, x, y, velocidade=80.0, amplitude_vertical=50.0, cor_base=(255, 255, 200)):
        """
        Args:
            x, y: Centro de flutuação no mundo
            velocidade: não usado (mantido por compatibilidade)
            amplitude_vertical: raio da área de flutuação
            cor_base: Cor RGB do vagalume
        """
        self.cx_base = float(x)  # Centro fixo de flutuação
        self.cy_base = float(y)
        self.x = float(x)
        self.y = float(y)
        self.x_inicio = float(x)
        self.y_inicio = float(y)
        self.velocidade = velocidade
        self.amplitude = amplitude_vertical
        self.cor_base = cor_base
        
        # Animação
        self.tempo = 0.0
        self.tamanho_base = 2
        self.tamanho_max = 4
        self.brilho_min = 180
        self.brilho_max = 255
        
        # Movimento orbital com duas frequências diferentes para parecer orgânico
        self.freq_1 = 0.18   # Frequência do loop principal
        self.freq_2 = 0.31   # Frequência secundária (número irracional relativo)
        self.raio_1 = amplitude_vertical * 0.6   # Raio do loop principal
        self.raio_2 = amplitude_vertical * 0.4   # Raio do desvio secundário
        self.fase = 0.0  # Fase inicial (varia por vagalume)
    
    def update(self, dt):
        """Atualiza posição com movimento orbital orgânico.
        
        Usa sobreposição de duas elipses rotacionando em frequências
        ligeiramente diferentes (Lissajous), criando trajetórias que
        nunca se repetem exatamente — efeito flutuante natural.
        """
        self.tempo += dt
        t = self.tempo
        
        # Loop principal: elipse rotacionando lentamente
        x1 = self.raio_1 * math.cos(2 * math.pi * self.freq_1 * t + self.fase)
        y1 = self.raio_1 * 0.55 * math.sin(2 * math.pi * self.freq_1 * t + self.fase)
        
        # Desvio secundário: elipse menor em frequência diferente
        x2 = self.raio_2 * math.cos(2 * math.pi * self.freq_2 * t + self.fase + math.pi / 3)
        y2 = self.raio_2 * 0.7 * math.sin(2 * math.pi * self.freq_2 * t + self.fase + math.pi / 3)
        
        self.x = self.cx_base + x1 + x2
        self.y = self.cy_base + y1 + y2
    
    def _get_tamanho_pulsante(self):
        """Calcula tamanho que pulsa com período de 1s."""
        pulsacao = 0.5 + 0.5 * math.sin(self.tempo * math.pi * 2)
        return int(self.tamanho_base + (self.tamanho_max - self.tamanho_base) * pulsacao)
    
    def _get_brilho_pulsante(self):
        """Calcula brilho que pulsa."""
        pulsacao = 0.5 + 0.5 * math.sin(self.tempo * math.pi * 2 + math.pi / 4)
        brilho = int(self.brilho_min + (self.brilho_max - self.brilho_min) * pulsacao)
        return max(0, min(255, brilho))
    
    def draw(self, screen, camera, viewport):
        """Renderiza o vagalume na tela.
        
        Usa:
        - desenhar_circulo para o halo amarelo
        - floodfill para brilho interior
        - Efeito de pulsação
        """
        # Culling simples
        if not (camera[0] <= self.x <= camera[2] and camera[1] <= self.y <= camera[3]):
            return
        
        # Converte coordenadas mundo → tela
        vx0, vy0, vx1, vy1 = viewport
        sx = vx0 + (self.x - camera[0]) / (camera[2] - camera[0]) * (vx1 - vx0)
        sy = vy0 + (self.y - camera[1]) / (camera[3] - camera[1]) * (vy1 - vy0)
        
        sx = int(sx)
        sy = int(sy)
        
        # Limita ao viewport
        if not (vx0 <= sx <= vx1 and vy0 <= sy <= vy1):
            return
        
        tamanho = self._get_tamanho_pulsante()
        brilho = self._get_brilho_pulsante()
        
        # Halo externo (círculo com brilho reduzido)
        cor_halo = (
            max(0, min(255, self.cor_base[0] - 80)),
            max(0, min(255, self.cor_base[1] - 80)),
            max(0, min(255, self.cor_base[2] - 120))
        )
        desenhar_circulo(screen, sx, sy, tamanho + 1, cor_halo)
        
        # Núcleo brilhante (círculo principal)
        cor_nucleo = (
            max(0, min(255, int(self.cor_base[0] * brilho / 255))),
            max(0, min(255, int(self.cor_base[1] * brilho / 255))),
            max(0, min(255, int(self.cor_base[2] * brilho / 255)))
        )
        desenhar_circulo(screen, sx, sy, tamanho, cor_nucleo)
        
        # Preenchimento interior com floodfill (efeito de brilho)
        cor_borda = cor_nucleo
        cor_fill = (
            max(0, min(255, self.cor_base[0])),
            max(0, min(255, self.cor_base[1])),
            min(255, self.cor_base[2])  # Verde mais forte para efeito vaga-lume
        )
        
        try:
            # Tenta preencher o interior do círculo
            # Pode falhar se a cor exata não existir no círculo
            flood_fill(screen, sx, sy, cor_fill, cor_borda)
        except Exception:
            # Se floodfill falhar, apenas deixa o círculo
            pass


class RebanhoVagalumes:
    """Gerencia múltiplos vagalumes em uma sala."""
    
    def __init__(self, quantidade=5, x_min=0, x_max=1600, y_min=200, y_max=600):
        """
        Args:
            quantidade: Número de vagalumes
            x_min, x_max: Limites horizontais da sala
            y_min, y_max: Limites verticais para geração
        """
        self.vagalumes = []
        self.x_max = x_max
        self.y_max = y_max
        
        # Cria vagalumes com centros espalhados pela sala
        import random
        for i in range(quantidade):
            # Centros distribuídos aleatoriamente na área passável
            x = x_min + random.uniform(0.1, 0.9) * (x_max - x_min)
            y = y_min + random.uniform(0.1, 0.9) * (y_max - y_min)
            
            # Raio de flutuação pequeno para manter orgânico e local
            amplitude = 30 + random.uniform(-5, 15)
            
            # Varia cor entre amarelo claro e branco-amarelado
            cores = [
                (255, 255, 180),  # Amarelo muito claro
                (255, 255, 220),  # Quase branco-amarelado
                (255, 245, 150),  # Amarelo dourado claro
            ]
            cor = random.choice(cores)
            
            vaga = Vagalume(x, y, amplitude_vertical=amplitude, cor_base=cor)
            # Fase inicial aleatória para cada vagalume não pulsar em sincronia
            vaga.fase = random.uniform(0, 2 * math.pi)
            vaga.freq_1 = 0.14 + random.uniform(-0.04, 0.06)
            vaga.freq_2 = 0.27 + random.uniform(-0.05, 0.08)
            self.vagalumes.append(vaga)
    
    def update(self, dt):
        """Atualiza todos os vagalumes."""
        for vaga in self.vagalumes:
            vaga.update(dt)
    
    def draw(self, screen, camera, viewport):
        """Renderiza todos os vagalumes."""
        for vaga in self.vagalumes:
            vaga.draw(screen, camera, viewport)
