from Validadores import *
from tkinter import messagebox
import mysql.connector

class Funcoes_sql(Validadores):

    def __init__(self, conex_dados, nome_tabela, nomes_colunas):
        self.HOST = conex_dados[0]
        self.USER = conex_dados[1]
        self.PASSWORD = conex_dados[2]
        self.DATABASE = conex_dados[3]
        self.NOME_TABELA = nome_tabela
        self.NOME_COLUNA = nomes_colunas

    def conexao(self):
        self.conn = mysql.connector.connect(
            host = self.HOST,
            user = self.USER,
            password= self.PASSWORD,
            database= self.DATABASE
        )
        self.cursor= self.conn.cursor()

    def get_data(self):
            self.conexao()
            self.cursor.execute(f"SELECT * FROM {self.NOME_TABELA}")
            data = self.cursor.fetchall()
            self.conn.commit()
            self.conn.close()
            return data

    def entry_ok(self, op, entrys):

        if self.tem_numero([entrys[1],entrys[2]]):            
            messagebox.showerror("ERRO!", f"'{self.NOME_COLUNA[1]}' e '{self.NOME_COLUNA[2]}' não pode ser um número!")
            return  False
        
        if op == "select":
            if self.espaco_vazio(entrys) <= 2:
                messagebox.showerror("ERRO! - Múltipla entrada", "Preencha apenas UMA entrada para a busca!")
                return False
            return True

        if self.espaco_vazio([entrys[1],entrys[2],entrys[3]]):
            messagebox.showerror("Erro!", "Por favor, preencha os espaços vazios!")
            return False
        
        
        if not self.so_numero(entrys[3]):
            messagebox.showerror("ERRO!", f"'{self.NOME_COLUNA[3]}' precisa ser um número!")
            return False
        
        if float(entrys[3]) > 99999.99:
            messagebox.showerror("ERRO!", f"'{self.NOME_COLUNA[3]}' não deve ser maior que R$99.999,99")
            return False
        
        if op == "insert":
            if not self.espaco_vazio(entrys[0]):
                messagebox.showinfo("Ops, entrada inválida", f"Deixa que eu cuido de {self.NOME_COLUNA[0]}")
        
        elif op == "delete":
            if not self.so_numero(entrys[0]):
                messagebox.showerror("ERRO!", f"'{self.NOME_COLUNA[0]}' precisa ser um número!")
                return False
        
        elif op == "update":
            if not self.so_numero(entrys[0]):
                messagebox.showerror("ERRO!", f"'{self.NOME_COLUNA[0]}' precisa ser um número!")
                return False

        return True

    def insert(self, entrys):
        if not self.entry_ok("insert", entrys): return False
        
        self.conexao()
        self.consulta =f"INSERT INTO {self.NOME_TABELA} ({self.NOME_COLUNA[0]},{self.NOME_COLUNA[1]},{self.NOME_COLUNA[2]},{self.NOME_COLUNA[3]})VALUES"+"(%s,%s,%s,%s)"
        self.valores=(None, entrys[1], entrys[2], entrys[3])
        
        try:
            self.cursor.execute(self.consulta,self.valores)
            self.conn.commit()
        except mysql.connector.errors.IntegrityError:      #previne erros como nomes(unique key) duplicados 
            messagebox.showerror(f"ERRO!", f"O {self.NOME_COLUNA[1]} '{entrys[1]}' já existe")
            self.conn.close()
            return False

        self.conn.close()
        return True
    

    def delete(self, entrys):
        if not self.entry_ok("delete", entrys): return False

        self.conexao()
        self.consulta = f"DELETE FROM {self.NOME_TABELA} WHERE {self.NOME_COLUNA[0]} = "+"%s"
        self.valores = [entrys[0]]

        try:
            self.cursor.execute(self.consulta,self.valores)
            self.conn.commit()
        except Exception:
            messagebox.showerror(f"ERRO!", "Erro Desconhecido")
            self.conn.close()
            return False

        self.conn.close()
        return True

    def update(self, entrys):
        if not self.entry_ok("update", entrys): return False

        self.conexao()
        self.consulta = f"UPDATE {self.NOME_TABELA} SET {self.NOME_COLUNA[1]} = "+"%s"+f", {self.NOME_COLUNA[2]} = "+"%s"+f", {self.NOME_COLUNA[3]} = "+"%s"+f" WHERE {self.NOME_COLUNA[0]} = "+"%s" #é feio, mas funciona kkk
        self.valores = (entrys[1], entrys[2], entrys[3], entrys[0])

        try:
            self.cursor.execute(self.consulta,self.valores)
        except mysql.connector.errors.IntegrityError as integrity_error:    #previne erros como um nome duplicado
            messagebox.showerror(f"ERRO! - {integrity_error.errno}", integrity_error.msg)
            self.conn.close()
            return

        self.conn.commit()
        self.conn.close()
        return True

    def select(self, entrys):

        if not self.entry_ok("select",entrys): return False
        entrys[0] = entrys[0].strip()   #STT-01

        if entrys[0] != "" and entrys[1] == "" and entrys[2] == "" and entrys[3] == "":            #busca por id
            self.consulta = f"SELECT * FROM {self.NOME_TABELA} WHERE {self.NOME_COLUNA[0]} LIKE "+"%s"+f" ORDER BY {self.NOME_COLUNA[0]} ASC"
            entrys[0] += '%'                                                                                   # o % permite a busca por resultados que comecem com o valor precedido
            self.valores = [entrys[0]]

        elif entrys[0] == "" and entrys[1] != "" and entrys[2] == "" and entrys[3] == "":            #busca por nome
            self.consulta = f"SELECT * FROM {self.NOME_TABELA} WHERE {self.NOME_COLUNA[1]} LIKE "+"%s"+f" ORDER BY {self.NOME_COLUNA[1]} ASC"
            entrys[1] = '%'+ entrys[1]
            entrys[1] += '%'
            self.valores = [entrys[1]]

        elif entrys[0] == "" and entrys[1] == "" and entrys[2] != "" and entrys[3] == "":            #busca por cargo
            self.consulta = f"SELECT * FROM {self.NOME_TABELA} WHERE {self.NOME_COLUNA[2]} LIKE "+"%s"+f" ORDER BY {self.NOME_COLUNA[2]} ASC"
            entrys[2] = '%'+ entrys[2]
            entrys[2] += '%'
            self.valores = [entrys[2]]

        elif entrys[0] == "" and entrys[1] == "" and entrys[2] == "" and entrys[3] != "":            #busca por salário
            self.consulta = f"SELECT * FROM {self.NOME_TABELA} WHERE {self.NOME_COLUNA[3]} >= "+"%s"+f" ORDER BY {self.NOME_COLUNA[3]} ASC"
            self.valores = [entrys[3]]
            
        self.conexao()
        self.cursor.execute(self.consulta, self.valores)
        encontrado = self.cursor.fetchall()
        self.conn.close()

        return encontrado
    
    
    #PRATO_PEDIDOS
    def delete_pratos_pedidos(self, entrys):
        #if not self.entry_ok("delete", entrys): return False

        self.conexao()
        self.consulta = f"DELETE FROM {self.NOME_TABELA} WHERE {self.NOME_COLUNA[0]} = "+"%s" + f"AND {self.NOME_COLUNA[1]} = "+"%s"
        self.valores = [entrys[0],entrys[1]]

        try:
            self.cursor.execute(self.consulta,self.valores)
            self.conn.commit()
        except Exception:
            messagebox.showerror(f"ERRO!", "Erro Desconhecido")
            self.conn.close()
            return False

        self.conn.close()
        return True
    
    def insert_pratos_pedidos(self, entrys):
        #if not self.entry_ok("insert", entrys): return False
        
        self.conexao()
        self.consulta =f"INSERT INTO {self.NOME_TABELA} ({self.NOME_COLUNA[0]},{self.NOME_COLUNA[1]},{self.NOME_COLUNA[2]})VALUES"+"(%s,%s,%s)"
        self.valores=(entrys[0], entrys[1], entrys[2])
        
        try:
            self.cursor.execute(self.consulta,self.valores)
            self.conn.commit()
        except mysql.connector.errors.IntegrityError:      #previne erros como nomes(unique key) duplicados 
            messagebox.showerror(f"ERRO!", f"O {self.NOME_COLUNA[1]} '{entrys[1]}' já existe")
            self.conn.close()
            return False

        self.conn.close()
        return True
    
    def update_pratos_pedidos(self, entrys):
        #if not self.entry_ok("update", entrys): return False

        self.conexao()
        self.consulta = f"UPDATE {self.NOME_TABELA} SET {self.NOME_COLUNA[2]} = "+"%s"+f" WHERE {self.NOME_COLUNA[0]} = "+"%s"+f"AND {self.NOME_COLUNA[1]} = "+"%s" #é feio, mas funciona kkk
        self.valores = (entrys[2], entrys[0], entrys[1])

        try:
            self.cursor.execute(self.consulta,self.valores)
        except mysql.connector.errors.IntegrityError as integrity_error:    #previne erros como um nome duplicado
            messagebox.showerror(f"ERRO! - {integrity_error.errno}", integrity_error.msg)
            self.conn.close()
            return

        self.conn.commit()
        self.conn.close()
        return True
    
    def select_pratos_pedidos(self,entrys):
        busca_cmd = "SELECT * FROM pratos_pedidos WHERE"
        and_flag = False

        if entrys[0] != "":
            busca_cmd += " id_pedido = " + f"'{entrys[0]}'"
            and_flag = True
        
        if entrys[1] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " id_prato = " + f"'{entrys[1]}'"
            and_flag = True

        if entrys[2] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " quantidade <= " + f"'{entrys[2]}'"
            and_flag = True


        if not and_flag:
            busca_cmd = "SELECT id_pedido,id_prato,quantidade FROM pratos_pedidos"

        self.conexao()
        self.cursor.execute(busca_cmd)
        data = self.cursor.fetchall()
        self.conn.commit()
        self.conn.close()
        return data
    
    #CARDÁPIOS
    
    def delete_cardapio(self, entrys):
        #if not self.entry_ok("delete", entrys): return False

        self.conexao()
        self.consulta = f"DELETE FROM {self.NOME_TABELA} WHERE {self.NOME_COLUNA[0]} = "+"%s"
        self.valores = [entrys[0]]

        try:
            self.cursor.execute(self.consulta,self.valores)
            self.conn.commit()
        except Exception:
            messagebox.showerror(f"ERRO!", "Erro Desconhecido")
            self.conn.close()
            return False

        self.conn.close()
        return True
    
    def insert_cardapio(self, entrys):
        #if not self.entry_ok("insert", entrys): return False
        
        self.conexao()
        self.consulta =f"INSERT INTO {self.NOME_TABELA} ({self.NOME_COLUNA[0]},{self.NOME_COLUNA[1]},{self.NOME_COLUNA[2]},{self.NOME_COLUNA[3]},{self.NOME_COLUNA[4]},{self.NOME_COLUNA[5]})VALUES"+"(%s,%s,%s,%s,%s,%s)"
        self.valores=(None, entrys[1], entrys[2], entrys[3], entrys[4], entrys[5])
        
        try:
            self.cursor.execute(self.consulta,self.valores)
            self.conn.commit()
        except mysql.connector.errors.IntegrityError:      #previne erros como nomes(unique key) duplicados 
            messagebox.showerror(f"ERRO!", f"O {self.NOME_COLUNA[1]} '{entrys[1]}' já existe")
            self.conn.close()
            return False

        self.conn.close()
        return True
    
    def update_cardapio(self, entrys):
        #if not self.entry_ok("update", entrys): return False

        self.conexao()
        self.consulta = f"UPDATE {self.NOME_TABELA} SET {self.NOME_COLUNA[1]} = "+"%s"+f",{self.NOME_COLUNA[2]} = "+"%s"+f",{self.NOME_COLUNA[3]} = "+"%s"+f",{self.NOME_COLUNA[4]} = "+"%s"+f",{self.NOME_COLUNA[5]} = "+"%s"+f" WHERE {self.NOME_COLUNA[0]} = "+"%s" 
        self.valores = (entrys[1], entrys[2], entrys[3],entrys[4],entrys[5],entrys[0])

        try:
            self.cursor.execute(self.consulta,self.valores)
        except mysql.connector.errors.IntegrityError as integrity_error:    #previne erros como um nome duplicado
            messagebox.showerror(f"ERRO! - {integrity_error.errno}", integrity_error.msg)
            self.conn.close()
            return

        self.conn.commit()
        self.conn.close()
        return True
    
    def select_cardapio(self,entrys):
        busca_cmd = "SELECT * FROM cardápio WHERE"
        and_flag = False

        if entrys[0] != "":
            busca_cmd += " id_prato = " + f"'{entrys[0]}'"
            and_flag = True
        
        if entrys[1] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " nome LIKE " + f"'%{entrys[1]}%'"
            and_flag = True

        if entrys[2] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " categoria LIKE " + f"'%{entrys[2]}%'"
            and_flag = True
        
        if entrys[3] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " descrição LIKE " + f"'%{entrys[3]}%'"
            and_flag = True

        if entrys[4] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " preço <= " + f"'{entrys[4]}'"
            and_flag = True


        if not and_flag:
            busca_cmd = "SELECT * FROM cardápio"

        self.conexao()
        self.cursor.execute(busca_cmd)
        data = self.cursor.fetchall()
        self.conn.commit()
        self.conn.close()
        return data
    
    
    #PEDIDOS
    def delete_pedidos(self, entrys):
        #if not self.entry_ok("delete", entrys): return False

        self.conexao()
        self.consulta = f"DELETE FROM {self.NOME_TABELA} WHERE {self.NOME_COLUNA[0]} = "+"%s"
        self.valores = [entrys[0]]

        try:
            self.cursor.execute(self.consulta,self.valores)
            self.conn.commit()
        except Exception:
            messagebox.showerror(f"ERRO!", "Erro Desconhecido")
            self.conn.close()
            return False

        self.conn.close()
        return True
    
    def insert_pedidos(self, entrys):
        #if not self.entry_ok("insert", entrys): return False
        
        self.conexao()
        self.consulta =f"INSERT INTO {self.NOME_TABELA} ({self.NOME_COLUNA[0]},{self.NOME_COLUNA[1]},{self.NOME_COLUNA[2]},{self.NOME_COLUNA[3]},{self.NOME_COLUNA[4]},{self.NOME_COLUNA[5]})VALUES"+"(%s,%s,%s,%s,%s,%s)"
        self.valores=(None, entrys[1], entrys[2], entrys[3], entrys[4], entrys[5])
        
        try:
            self.cursor.execute(self.consulta,self.valores)
            self.conn.commit()
        except mysql.connector.errors.IntegrityError as e:     #previne erros como nomes(unique key) duplicados 
            #messagebox.showerror(f"ERRO!", f"O {self.NOME_COLUNA[1]} '{entrys[1]}' já existe")
            print(e)
            
            self.conn.close()
            return False

        self.conn.close()
        return True
    
    def update_pedidos(self, entrys):
        #if not self.entry_ok("update", entrys): return False

        self.conexao()
        self.consulta = f"UPDATE {self.NOME_TABELA} SET {self.NOME_COLUNA[1]} = "+"%s"+f",{self.NOME_COLUNA[2]} = "+"%s"+f",{self.NOME_COLUNA[3]} = "+"%s"+f",{self.NOME_COLUNA[4]} = "+"%s"+f",{self.NOME_COLUNA[5]} = "+"%s"+f",{self.NOME_COLUNA[6]} = "+"%s"+f" WHERE {self.NOME_COLUNA[0]} = "+"%s" 
        self.valores = (entrys[1], entrys[2], entrys[3],entrys[4],entrys[5],entrys[6],entrys[0])

        try:
            self.cursor.execute(self.consulta,self.valores)
        except mysql.connector.errors.IntegrityError as integrity_error:    #previne erros como um nome duplicado
            messagebox.showerror(f"ERRO! - {integrity_error.errno}", integrity_error.msg)
            self.conn.close()
            return

        self.conn.commit()
        self.conn.close()
        return True
    
    def select_pedidos(self,entrys):
        busca_cmd = "SELECT * FROM pedidos WHERE"
        and_flag = False

        if entrys[0] != "":
            busca_cmd += " id_pedido = " + f"'{entrys[0]}'"
            and_flag = True
        
        if entrys[1] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " id_cliente = " + f"'{entrys[1]}'"
            and_flag = True

        if entrys[2] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " id_funcionário " + f"'{entrys[2]}'"
            and_flag = True
        
        if entrys[3] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " total <= " + f"'{entrys[3]}'"
            and_flag = True

        if entrys[4] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " pagamento LIKE " + f"'%{entrys[4]}%'"
            and_flag = True
        
        if entrys[5] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " situação LIKE " + f"'%{entrys[5]}%'"
            and_flag = True

        if entrys[6] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " data_pedido LIKE " + f"'%{entrys[6]}%'"
            and_flag = True

        if not and_flag:
            busca_cmd = "SELECT * FROM pedidos"


        self.conexao()
        self.cursor.execute(busca_cmd)
        data = self.cursor.fetchall()
        self.conn.commit()
        self.conn.close()
        return data
    
    #Clientes
    
    def delete_clientes(self, entrys):
        #if not self.entry_ok("delete", entrys): return False

        self.conexao()
        self.cursor.callproc("delete_cliente", [entrys[0]])
        self.conn.commit()

        self.conn.close()
        return True
    
    def insert_clientes(self, entrys):
        #if not self.entry_ok("insert", entrys): return False
        
        self.conexao()
        self.cursor.callproc("inserir_cliente", [entrys[1],entrys[2],entrys[3]])
        self.conn.commit()
        
        self.conn.close()
        return True
    
    def update_clientes(self, entrys):
        #if not self.entry_ok("update", entrys): return False

        self.conexao()
        self.consulta = f"UPDATE {self.NOME_TABELA} SET {self.NOME_COLUNA[1]} = "+"%s"+f",{self.NOME_COLUNA[2]} = "+"%s"+f",{self.NOME_COLUNA[3]} = "+"%s"+f" WHERE {self.NOME_COLUNA[0]} = "+"%s" 
        self.valores = (entrys[1], entrys[2], entrys[3],entrys[0])

        try:
            self.cursor.execute(self.consulta,self.valores)
        except mysql.connector.errors.IntegrityError as integrity_error:    #previne erros como um nome duplicado
            messagebox.showerror(f"ERRO! - {integrity_error.errno}", integrity_error.msg)
            self.conn.close()
            return

        self.conn.commit()
        self.conn.close()
        return True
    
    def select_clientes(self,entrys):
        busca_cmd = "SELECT * FROM clientes WHERE"
        and_flag = False

        if entrys[0] != "":
            busca_cmd += " id_cliente = " + f"'{entrys[0]}'"
            and_flag = True
        
        if entrys[1] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " nome LIKE " + f"'%{entrys[1]}%'"
            and_flag = True

        if entrys[2] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " telefone LIKE " + f"'%{entrys[2]}%'"
            and_flag = True
        
        if entrys[3] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " desconto = " + f"'{entrys[3]}'"
            and_flag = True


        if not and_flag:
            busca_cmd = "SELECT * FROM clientes"


        self.conexao()
        self.cursor.execute(busca_cmd)
        data = self.cursor.fetchall()
        self.conn.commit()
        self.conn.close()
        return data
    
    #FUNCIONÁRIO

    def delete_funcionario(self, entrys):
        #if not self.entry_ok("delete", entrys): return False

        self.conexao()
        self.cursor.callproc("delete_funcionario", [entrys[0]])
        self.conn.commit()

        self.conn.close()
        return True
    
    def insert_funcionario(self, entrys):
        #if not self.entry_ok("insert", entrys): return False
        
        self.conexao()
        self.cursor.callproc("inserir_funcionario", [entrys[1],entrys[2],entrys[3]])
        self.conn.commit()
        
        self.conn.close()
        return True
    
    def update_funcionario(self, entrys):
        #if not self.entry_ok("update", entrys): return False

        self.conexao()
        self.consulta = f"UPDATE {self.NOME_TABELA} SET {self.NOME_COLUNA[1]} = "+"%s"+f",{self.NOME_COLUNA[2]} = "+"%s"+f",{self.NOME_COLUNA[3]} = "+"%s"+f" WHERE {self.NOME_COLUNA[0]} = "+"%s" 
        self.valores = (entrys[1], entrys[2], entrys[3],entrys[0])

        
        self.cursor.execute(self.consulta,self.valores)
        

        self.conn.commit()
        self.conn.close()
        return True
    
    def select_funcionario(self,entrys):
        busca_cmd = "SELECT * FROM funcionários WHERE"
        and_flag = False

        if entrys[0] != "":
            busca_cmd += " id_funcionário = " + f"'{entrys[0]}'"
            and_flag = True
        
        if entrys[1] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " nome LIKE " + f"'%{entrys[1]}%'"
            and_flag = True

        if entrys[2] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " cargo LIKE " + f"'%{entrys[2]}%'"
            and_flag = True
        
        if entrys[3] != "":
            if and_flag:
                busca_cmd += " AND"
            busca_cmd += " salário <= " + f"'{entrys[3]}'"
            and_flag = True


        if not and_flag:
            busca_cmd = "SELECT * FROM funcionários"


        self.conexao()
        self.cursor.execute(busca_cmd)
        data = self.cursor.fetchall()
        self.conn.commit()
        self.conn.close()
        return data
        
