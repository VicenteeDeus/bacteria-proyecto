import random
import pandas as pd
import uuid
from enum import Enum


class Tipo_Bacteria(Enum):
    ACTIVA = 1
    MUERTA = 2
    RESISTENTE = 3
    BIOFILM = 4

# Eventos probabilisticos
def aplicar_antibiotico(bacteria):
  if not bacteria.resistente:
      # 15% de probabilidad de que la bacteria muera si no es resistente
      probabilidad_supervivencia = 0.15
      if random.random() < probabilidad_supervivencia:
          bacteria.morir()
          print(f"Bacteria {bacteria.id} muere por antibiótico.")
          return True
      else:
          print(f"Bacteria {bacteria.id} sobrevive al antibiótico.")
          return False

def consumo_de_nutrientes(a=0, b=0):
  energia_consumo = random.randint(a, b) # Distribución uniforme entre a y b
  return energia_consumo

class Bacteria:
  def __init__(self, pos=None, raza=None, energia=0, resistente=False, isBiofilm = False, estado='activa'):
    self.pos = pos # (tupla)
    self.id = uuid.uuid4() # Genera un ID único para la bacteria
    self.raza = raza # Tipo de bacteria (por ejemplo, 'E. coli', 'Staphylococcus', etc.)
                     # dependiendo de la raza posee diferente energía minima de dividirse,
                     # energia minima necesaria para vivir
    self.energia = energia
    self.resistente = resistente
    self.estado = estado
    self.isBiofilm = isBiofilm

  def alimentar(self, nutrientes): 
    energia = consumo_de_nutrientes(b=nutrientes)
    self.energia += energia
    return energia # retorna la energia consumida

  def dividirse(self, div_energia):
    if self.energia >= div_energia:
      # Supongamos que se necesita 10 de energía para dividirse
      nueva_bacteria = Bacteria(
                        raza=self.raza, 
                        energia=self.energia // 2, 
                        resistente=self.resistente,
                        isBiofilm=self.isBiofilm
                       )
      self.energia //= 2  # La bacteria madre pierde la mitad de su energía
      return nueva_bacteria
    return None

  def mutar(self):
    if not self.resistente:
        # 10% de probabilidad de que la bacteria se vuelva resistente
        if random.random() < 0.15:
            self.resistente = True
            print(f"Bacteria {self.id} se ha vuelto resistente.")
        else:
            print(f"Bacteria {self.id} no muta a resistente.")

  def morir(self):
    self.estado = 'muerta'

class Ambiente:
  def __init__(self, grilla, nutrientes, factor_ambiental):
    self.grilla = grilla
    self.nutrientes = nutrientes
    self.factor_ambiental = factor_ambiental
  
  def actualizar_nutrientes(self, pos, nutrientes): # Actualizar los nutrientes en cada paso
    i, j = pos
    self.nutrientes[i, j] -= nutrientes 

  def actualizar_grilla(self, pos, bacteria):
    i, j = pos
    if bacteria.estado == "muerta":
      self.grilla[i, j] = Tipo_Bacteria.MUERTA.value
    elif bacteria.isBiofilm:
      self.grilla[i, j] = Tipo_Bacteria.BIOFILM.value
    elif bacteria.resistente:
      self.grilla[i, j] = Tipo_Bacteria.RESISTENTE.value
    else:
      self.grilla[i, j] = Tipo_Bacteria.ACTIVA.value
    
  def difundir_bacterias(self, total_biofilm, total_muertas, total_activas, ini_energia):
    # Rellenar la grilla con el total de biofilm, muertas y activas aleatoriamente
    # Primero, crear una lista de todas las posiciones posibles
    posiciones = [(i, j) for i in range(self.grilla.shape[0]) for j in range(self.grilla.shape[1])]
    random.shuffle(posiciones) # Esto reordena la lista posiciones de manera aleatoria en el lugar (no devuelve una nueva lista, modifica la existente).
    bacterias = []

    idx = 0
    # Colocar biofilm (4)
    for _ in range(int(total_biofilm)):
      if idx < len(posiciones):
        i, j = posiciones[idx]
        self.grilla[i, j] = Tipo_Bacteria.BIOFILM.value
        bacterias.append(
          Bacteria(
            pos = (i,j),
            raza = random.choice(['E. coli', 'Staphylococcus', 'Salmonella']),
            energia = ini_energia, 
            resistente = True, # Las bacterias de biofilm poseen resistencia 
            estado = 'activa',# bacterias biofilm están activas 
            isBiofilm = True
          )
        )
        idx += 1
    # Colocar muertas (2)
    for _ in range(int(total_muertas)):
      if idx < len(posiciones):
        i, j = posiciones[idx]
        self.grilla[i, j] = Tipo_Bacteria.MUERTA.value
        bacterias.append(
          Bacteria(
            pos = (i,j),
            raza = random.choice(['E. coli', 'Staphylococcus', 'Salmonella']),
            energia = 0,  # Las bacterias muertas poseen energia 0
            resistente = False, # Las bacterias muertas no poseen resistencia 
            estado = 'muerta',
            isBiofilm = False
          )
        )
        idx += 1
    # Colocar activas (1)
    for _ in range(int(total_activas)):
      if idx < len(posiciones):
        i, j = posiciones[idx]
        self.grilla[i, j] = Tipo_Bacteria.ACTIVA.value
        bacterias.append(
          Bacteria(
            pos = (i,j),
            raza = random.choice(['E. coli', 'Staphylococcus', 'Salmonella']),
            energia = ini_energia, 
            resistente = False, # Las bacterias de biofilm poseen resistencia 
            estado = 'activa',# bacterias biofilm están activas 
            isBiofilm = False
          )
        )
        idx += 1
    # El resto queda en 0 (vacío)
    return bacterias 

  def difundir_factor_ambiental(self):
    # Rellenar la grilla de factores ambientales con 0 (normal) o 1 (antibiótico)
    for i in range(self.factor_ambiental.shape[0]):
      for j in range(self.factor_ambiental.shape[1]):
        self.factor_ambiental[i, j] = random.choice([0, 1])  
  
  def difundir_nutrientes(self): # Difundir inicialmente los nutrientes sobre la grilla de nutrientes
    # Rellenar la grilla de nutrientes con valores aleatorios entre 5 y 40
    for i in range(self.nutrientes.shape[0]):
      for j in range(self.nutrientes.shape[1]):
        self.nutrientes[i, j] = random.randint(5, 40)

  def get_espacio(self, pos): # Verifica si hay espacio para la bacteria para dividirse si es así devuelve la posición
    i, j = pos
    values = [(i+1, j), (i-1,j), (i, j-1), (i,j+1)]
    for k,z  in values:
      try: 
        if self.grilla[k, z] == 0:
          return (k, z)
      except IndexError:
        continue
    return None

  def get_factor(self, pos):
    i, j = pos
    if self.factor_ambiental[i,j] == 1:
      return True
    else:
      return False
      
  def aplicar_ambiente(self): # Aplicar ambiente en la gráfica en cada paso 
    # Retorna la grilla
    return self.grilla

class Colonia:
  # datos = {
  #   1: [arrBacteria, ...],  ## arrBacteria = [id, raza, energia, resistente, estado, isBiofilm]
  #   2: ...
  # }
  datos = {}
  paso_actual = 0

  def __init__(self, bacterias=[], ambiente=None, div_energia=10, pasos_totales=0):
    self.bacterias = bacterias
    self.ambiente = ambiente
    self.div_energia = div_energia
    self.pasos_totales = pasos_totales

  def set_bacterias(self, bacterias):
    self.bacterias = bacterias
  
  def set_ambiente(self, ambiente):
    self.ambiente = ambiente 

  def set_div_energia(self, div_energia):
    self.div_energia = div_energia

  def set_pasos_totales(self, pasos_totales):
    for i in range(1,pasos_totales+1):
      self.datos[i] = []
    self.pasos_totales = pasos_totales
    
  def paso(self):
    self.paso_actual += 1
 
    new_arr_bacterias = []
    for bacteria in self.bacterias:
      i, j = bacteria.pos

      # Verificar factor ambiental
      if self.ambiente.get_factor(bacteria.pos):
        if aplicar_antibiotico(bacteria):
          self.ambiente.actualizar_grilla(bacteria.pos, bacteria)

      if bacteria.estado == 'activa':
        # verificar nutrientes
        nutrientes = self.ambiente.nutrientes[i,j]
        if nutrientes > 0:
          nutrientes_consumidos = bacteria.alimentar(nutrientes)
          self.ambiente.actualizar_nutrientes((i, j), nutrientes_consumidos)
        # La bacteria tiene espacio para dividirse?
        espacio = self.ambiente.get_espacio(bacteria.pos)
        
        if espacio:
          # división de bacteria si alcanza un umbral de energía
          new_bacteria = bacteria.dividirse(self.div_energia)
          if new_bacteria:  # Si ocurre la división
            bacteria.mutar()  
            new_bacteria.mutar() 
            # Incluir la nueva bacteria en la grilla
            self.ambiente.actualizar_grilla(espacio, new_bacteria)
            # Actualizar posición de la bacteria
            new_bacteria.pos = espacio
            # incluir en nuevo arreglo
            new_arr_bacterias.append(new_bacteria)
            # Agregar bacteria al registro de pasos
            print("paso actual: ", self.paso_actual)
            self.datos[self.paso_actual].append([
              self.paso_actual,         # Posición de la bacteria
              new_bacteria.id,          # ID de la bacteria 
              new_bacteria.raza,        # Raza de la bacteria
              new_bacteria.energia,     # Energía de la bacteria
              new_bacteria.resistente,  # Si es resistente o no
              new_bacteria.estado,      # Estado de la bacteria (activa, muerta, etc.)
              new_bacteria.isBiofilm    # Si es biofilm o no
            ])

      # enegia minima necesaria para vivir
      energia_minima = 5
      if bacteria.energia < energia_minima:
        bacteria.morir()
        self.ambiente.actualizar_grilla(bacteria.pos, bacteria)
      
      # Pasar copia al arreglo de datos
      self.datos[self.paso_actual].append([
        self.paso_actual,         # Posición de la bacteria
        bacteria.id,          # ID de la bacteria 
        bacteria.raza,        # Raza de la bacteria
        bacteria.energia,     # Energía de la bacteria
        bacteria.resistente,  # Si es resistente o no
        bacteria.estado,      # Estado de la bacteria (activa, muerta, etc.)
        bacteria.isBiofilm    # Si es biofilm o no
      ])

    self.bacterias += new_arr_bacterias

    return (self.ambiente.aplicar_ambiente(), self.paso_actual)

  def reporte_estado(self):
    print("Estado de la colonia:")
    print(f"Paso actual", self.paso_actual)
    for bacteria in self.bacterias:
      print(f"ID: {bacteria.id}, Raza: {bacteria.raza}, Energía: {bacteria.energia}, Resistente: {bacteria.resistente}, Estado: {bacteria.estado}")
  
  def exportar_csv(self, button):
    data_aux = []
    for arreglos in self.datos.values():
      for arr in arreglos:
        data_aux.append(arr)

    df = pd.DataFrame(data_aux, columns=["Paso", "ID", "Raza", "Energía", "Resistente", "Estado", "isBioFilm"])
    df.to_csv("bacterias.csv", index=False, encoding="utf-8") 
