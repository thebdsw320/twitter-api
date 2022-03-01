import pymysql as ps

class Productos:
    def iniciar_conexion(self):
        self.conexion = ps.connect(host='localhost',
                                   user='bdsw320',
                                   password='password',
                                   database='productos')
        
        return self.conexion
    
    def crear(self, nombre, categoria, uid, color, precio):
        self.conexion = self.iniciar_conexion()
        self.cursor = self.conexion.cursor()
        
        sentencia_sql = f'INSERT INTO productos VALUES ("{nombre}", "{categoria}", "{uid}", "{color}", {precio})'
        
        self.cursor.execute(sentencia_sql)
        self.conexion.commit()