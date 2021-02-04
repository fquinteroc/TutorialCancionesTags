import unittest

from src.logica.coleccion import Coleccion
from src.modelo.album import Album
from src.modelo.cancion import Cancion
from src.modelo.declarative_base import Session
from src.modelo.interprete import Interprete


class CancionTestCase(unittest.TestCase):

    def setUp(self):
        self.session = Session()
        self.coleccion = Coleccion()

    def test_dar_cancion_por_id(self):
        cancion = self.session.query(Cancion).filter(Cancion.titulo == "Baby blues").first()
        if cancion is None:
            nuevo_album = Album(titulo="Amapola azul", ano=2020, descripcion="Instrumental", medio="CD")
            nuevo_interprete = Interprete(nombre="Andrea Echeverri", texto_curiosidades="En ese año nacio su hijo...",
                                          cancion=-1)
            nueva_cancion = Cancion(titulo="Baby blues", minutos=3, segundos=20, compositor="Desconocido",
                                    albumes=[nuevo_album])
            nueva_cancion.interpretes.append(nuevo_interprete)
            nuevo_interprete.cancion = nueva_cancion.id
            self.session.add(nuevo_album)
            self.session.add(nuevo_interprete)
            self.session.add(nueva_cancion)
            self.session.commit()
            consulta = self.coleccion.dar_cancion_por_id(nueva_cancion.id)
        else:
            consulta = self.coleccion.dar_cancion_por_id(cancion.id)
        self.assertIsNotNone(consulta)

    def test_buscar_canciones_por_titulo(self):
        cancion = self.session.query(Cancion).filter(Cancion.titulo == "Express Yourself").first()
        if cancion is None:
            nuevo_album = Album(titulo="Like a Prayer", ano=1989, descripcion="Sin descripción", medio="CASETE")
            nuevo_interprete = Interprete(nombre="Madona",
                                          texto_curiosidades="Publicado por la compañía discográfica Sire Records",
                                          cancion=-1)
            nueva_cancion = Cancion(titulo="Express Yourself", minutos=4, segundos=39,
                                    compositor="Stephen Bray y otros",
                                    albumes=[nuevo_album])
            nueva_cancion.interpretes.append(nuevo_interprete)
            nuevo_interprete.cancion = nueva_cancion.id
            self.session.add(nuevo_album)
            self.session.add(nuevo_interprete)
            self.session.add(nueva_cancion)
            self.session.commit()
        consulta = self.coleccion.buscar_canciones_por_titulo("Expr")
        self.assertEqual(len(consulta), 1)

    def test_editar_cancion(self):
        cancion = self.session.query(Cancion).filter(Cancion.titulo == "Express Yourself").first()
        interprete = self.session.query(Interprete).filter(Interprete.nombre == "Madona").first()
        if cancion is not None:
            self.coleccion.editar_cancion(cancion.id, "Express Yourself", 2, 54, "Patrick Leonard y otros",
                                          [{'id': interprete.id, 'nombre': 'Madona',
                                            'texto_curiosidades': 'Publicado por la compañía discográfica Sire Records'}])
            consulta = self.session.query(Cancion).filter(Cancion.compositor == "Patrick Leonard y otros").first()
            self.assertIsNotNone(consulta)

    def test_eliminar_cancion(self):
        self.coleccion.eliminar_cancion(1)
        consulta = self.session.query(Cancion).filter(Cancion.id == 1).first()
        self.assertIsNone(consulta)

    def test_cancion_sin_interpretes(self):
        cancion = self.coleccion.agregar_cancion("Felicidad", 3, 10, "Desconocido", -1, [])
        self.assertEqual(cancion, False)

    def test_cancion_varios_interpretes(self):
        self.coleccion.agregar_interprete("Vicente Fernandez", "Grabado en 3 potrillos", -1)
        self.coleccion.agregar_interprete("Alejandro Fernandez", "En honor al aniversario...", -1)
        self.coleccion.agregar_cancion("Felicidad", 4, 37, "Desconocido", -1,
                                       [{'nombre': 'Vicente Fernandez', 'texto_curiosidades': 'Grabado en 3 potrillos'},
                                        {'nombre': 'Alejandro Fernandez',
                                         'texto_curiosidades': 'En honor al aniversario...'}])
        consulta = self.session.query(Cancion).filter(Cancion.titulo == "Felicidad").first()
        self.assertIsNotNone(consulta)

    def test_cancion_con_album(self):
        self.coleccion.agregar_album("Renacer", 2005, "Sin descripción", "CD")
        consulta1 = self.session.query(Album).filter(Album.titulo == "Renacer").first().id
        self.coleccion.agregar_interprete("Alejandra Guzman", "Canción dedicada a su ...", -1)
        self.coleccion.agregar_cancion("Bye mamá", 1, 48, "Desconocido", consulta1,
                                       [{'nombre': 'Alejandra Guzman',
                                         'texto_curiosidades': 'Canción dedicada a su ...'}])
        consulta2 = self.session.query(Cancion).filter(Cancion.titulo == "Bye mamá").first()
        self.assertNotEqual(len(consulta2.albumes), 0)

    def test_cancion_repetida_album(self):
        self.coleccion.agregar_album("25", 2015, "Sin descripción", "CD")
        consulta1 = self.session.query(Album).filter(Album.titulo == "25").first().id
        self.coleccion.agregar_interprete("Adele", "Premio Grammy a la mejor grabación del año", -1)
        cancion1 = self.coleccion.agregar_cancion("Hello", 3, 45, "Desconocido", consulta1,
                                                  [{'nombre': 'Adele',
                                                    'texto_curiosidades': 'Premio Grammy a la mejor grabación del año'}])
        self.coleccion.agregar_interprete("Queen", "Premio Grammy a la mejor grabación del año", -1)
        cancion2 = self.coleccion.agregar_cancion("Hello", 5, 55, "Desconocido", consulta1,
                                                  [{'nombre': 'Queen',
                                                    'texto_curiosidades': 'Canción demasiado larga para la época'}])
        self.assertEqual(cancion2, False)
