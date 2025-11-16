# Módulo principal do Sistema Acadêmico Colaborativo. 
# OBSERVAÇÃO: Trocar o diretório de acordo com o seu PC para ler os arquivos CSV.

# import tkinter as tk, csv, os, hashlib, time
from tkinter import ttk, messagebox, simpledialog

# ==============================================================================
# 1. CONFIGURAÇÕES E CONSTANTES (Estrutura do Projeto)
# ==============================================================================

# Definição do diretório base para salvar os arquivos CSV (Ajuste este caminho se necessário)
BASE = r"C:\Users\Vitor Moura\Desktop\PIM OFICIAL\output"

# Caminhos dos arquivos CSV (Banco de Dados)
ARQ_USU=os.path.join(BASE,"usuarios.csv")     # Usuários do sistema (login, senha, tipo)
ARQ_ALUN=os.path.join(BASE,"alunos.csv")      # Dados dos Alunos
ARQ_TURM=os.path.join(BASE,"turmas.csv")      # Cadastro de Turmas
ARQ_ATIV=os.path.join(BASE,"atividades.csv")  # Atividades criadas pelos Professores
ARQ_NOTA=os.path.join(BASE,"notas.csv")       # Notas atribuídas aos Alunos
ARQ_ENTREGA=os.path.join(BASE,"entregas.csv") # Entregas de atividades feitas pelos Alunos

# Listas de Disciplinas e Fieldnames (Cabeçalhos do CSV)
DISCIPLINAS=["Matemática","Português","Física","Ciências","História"]
ATIV_FIELDS=["id_atividade","disciplina","descricao","id_professor","id_turma"]
ENTREGA_FIELDS=["id_atividade","id_aluno","nome_aluno","data_entrega","resposta"]
ALUN_FIELDS=["id","nome","email","id_turma"]
TURM_FIELDS=["id_turma","nome_turma"]

# ==============================================================================
# 2. FUNÇÕES DE PERSISTÊNCIA (CRUD em CSV)
# ==============================================================================

def ler_csv(path):
    """Lê um arquivo CSV, retorna uma lista de dicionários ou uma lista vazia."""
    os.makedirs(os.path.dirname(path),exist_ok=True);
    if not os.path.exists(path) or os.stat(path).st_size==0: return []
    with open(path,newline="",encoding="utf-8") as f: return list(csv.DictReader(f,delimiter=";"))

def _ensure_csv_header(path,fieldnames):
    """Garante que o cabeçalho do CSV exista, escrevendo-o se o arquivo for novo/vazio."""
    os.makedirs(os.path.dirname(path),exist_ok=True)
    if not os.path.exists(path) or os.stat(path).st_size==0:
        with open(path,'w',newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=fieldnames,delimiter=";"); w.writeheader()

def escrever_csv(path,fieldnames,rows):
    """Sobrescreve (rewrite) o arquivo CSV com a lista de linhas (usado para atualizações/exclusões)."""
    with open(path,'w',newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fieldnames,delimiter=";")
        w.writeheader() # Garante que o cabeçalho seja reescrito
        if isinstance(rows,dict): rows=[rows]
        w.writerows(rows) # Salva todos os dados com quebras de linha corretas

def append_csv(path,row,fieldnames):
    """Adiciona um novo registro (append) ao final do arquivo CSV."""
    _ensure_csv_header(path,fieldnames)
    with open(path,'a',newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fieldnames,delimiter=";")
        if isinstance(row,dict): row=[row]
        w.writerows(row) # Adiciona o novo registro

def get_entregues_ids(aluno_id):
    """Retorna um conjunto de IDs de atividades que o aluno já entregou."""
    return {e.get("id_atividade") for e in ler_csv(ARQ_ENTREGA) if e.get("id_aluno")==aluno_id}

# ==============================================================================
# 3. CLASSE PRINCIPAL DA APLICAÇÃO (App)
# ==============================================================================
class App:
    def __init__(self,root):
        """Inicializa a aplicação, estilos e verifica/cria os arquivos de dados."""
        self.root=root; root.title("Sistema Acadêmico - PIM"); root.geometry("850x550")
        self.setup_styles(); self.usuario=None; self.lastmt={} # Inicializa estilos, usuário e dicionário de last modification time
        
        # Garante que todos os arquivos de dados existam com seus cabeçalhos.
        _ensure_csv_header(ARQ_ALUN,ALUN_FIELDS); _ensure_csv_header(ARQ_TURM,TURM_FIELDS)
        _ensure_csv_header(ARQ_ATIV,ATIV_FIELDS); _ensure_csv_header(ARQ_ENTREGA,ENTREGA_FIELDS)
        _ensure_csv_header(ARQ_USU,["login","senha","tipo"]); _ensure_csv_header(ARQ_NOTA,["id_aluno","disciplina","nota"])
        
        # Registra o tempo de última modificação de cada arquivo para o poll
        for p in [ARQ_USU,ARQ_ALUN,ARQ_TURM,ARQ_ATIV,ARQ_NOTA,ARQ_ENTREGA]: self.lastmt[p]=os.path.getmtime(p) if os.path.exists(p) else 0
        
        self.build_login(); self.poll() # Constrói a tela de login e inicia a verificação de updates

    def setup_styles(self):
        """Define e configura os estilos visuais (cores e fontes) dos widgets."""
        style=ttk.Style(self.root); style.theme_use("clam")
        primary_color="#007bff"; success_color="#28a745"; danger_color="#dc3545"; light_bg="#f8f9fa"
        # Configura estilos para Títulos e Botões (Primary, Success, Danger)
        style.configure('Titre.TLabel',font=("Arial",20,"bold"),foreground=primary_color)
        style.configure('Primary.TButton',font=('Arial',10,'bold'),foreground='white',background=primary_color,padding=[10,5])
        style.map('Primary.TButton',background=[('active','#0056b3')],foreground=[('disabled','gray')])
        style.configure('Success.TButton',font=('Arial',10,'bold'),foreground='white',background=success_color,padding=[10,5])
        style.map('Success.TButton',background=[('active','#1e7e34')])
        style.configure('Danger.TButton',font=('Arial',10,'bold'),foreground='white',background=danger_color,padding=[10,5])
        style.map('Danger.TButton',background=[('active','#bd2130')])
        style.configure('Content.TFrame',background=light_bg)

    def poll(self):
        """Verifica periodicamente (a cada 2s) se os arquivos de dados foram alterados, recarregando a tela se necessário."""
        updated=any(os.path.exists(p) and os.path.getmtime(p)!=self.lastmt[p] for p in self.lastmt)
        for p in self.lastmt: self.lastmt[p]=os.path.getmtime(p) if os.path.exists(p) else 0
        if updated and self.usuario: # Se houve update e o usuário está logado
            typ=self.usuario["tipo"]; login=self.usuario["login"]
            # Recarrega a tela do perfil para exibir novos dados/mudanças
            if typ.startswith("aluno"): self.show_aluno(login)
            elif typ.startswith("prof"): self.show_prof(login)
            elif typ.startswith("coord"): self.show_coord(login)
            elif typ.startswith("adm") or typ.startswith("tecnico"): self.show_adm(login)
        self.root.after(2000,self.poll) # Chama a si mesmo a cada 2000ms

    def clear(self):
        """Remove todos os widgets da janela principal para trocar de tela."""
        for w in self.root.winfo_children(): w.destroy()

    # --- Métodos de Login/Logout ---
    def build_login(self):
        """Constrói a interface de login."""
        self.clear()
        main_frame=ttk.Frame(self.root,padding="40 60 40 40",style='Content.TFrame')
        main_frame.place(relx=0.5,rely=0.5,anchor=tk.CENTER)
        ttk.Label(main_frame,text="Sistema Acadêmico - Login",style='Titre.TLabel').pack(pady=20)
        input_frame=ttk.Frame(main_frame,padding=10); input_frame.pack(fill="x",padx=20)
        ttk.Label(input_frame,text="Usuário:",font=('Arial',10,'bold')).pack(anchor="w",pady=(5,0))
        self.e_user=ttk.Entry(input_frame,width=30); self.e_user.pack(fill="x",ipady=4)
        ttk.Label(input_frame,text="Senha:",font=('Arial',10,'bold')).pack(anchor="w",pady=(10,0))
        self.e_pass=ttk.Entry(input_frame,show="*",width=30); self.e_pass.pack(fill="x",ipady=4)
        ttk.Button(main_frame,text="Entrar",command=self.do_login,style='Success.TButton').pack(pady=20,fill="x",padx=30)

    def do_login(self):
        """Processa a tentativa de login, verifica credenciais e direciona para o perfil."""
        u,s=self.e_user.get().strip(),self.e_pass.get().strip()
        for row in ler_csv(ARQ_USU):
            if row.get("login")==u and row.get("senha")==s: # Credenciais OK
                self.usuario=row; typ=row.get("tipo")
                # Direciona para a tela do perfil correspondente
                if typ.startswith("aluno"): self.show_aluno(u)
                elif typ.startswith("prof"): self.show_prof(u)
                elif typ.startswith("coord"): self.show_coord(u)
                elif typ.startswith("adm") or typ.startswith("tecnico"): self.show_adm(u)
                return
        messagebox.showerror("Erro","Usuário ou senha incorretos.")

    def logout(self):
        """Limpa a sessão do usuário e volta para a tela de login."""
        self.usuario=None; self.root.geometry("850x550"); self.build_login()

    # ==============================================================================
    # 4. ÁREA DO ALUNO
    # ==============================================================================
    def get_aluno_info(self,login):
        """Busca o registro completo do aluno logado usando login (email/nome) no arquivo alunos.csv."""
        return next((a for a in ler_csv(ARQ_ALUN) if login in a.get("email","") or login.lower() in a.get("nome","").lower()),None)

    def show_aluno(self,login):
        """Constrói a interface principal para o Aluno."""
        self.clear()
        main_frame=ttk.Frame(self.root,padding="20",style='Content.TFrame'); main_frame.pack(fill="both",expand=True)
        ttk.Label(main_frame,text="Área do Aluno",style='Titre.TLabel').pack(pady=15)
        aluno=self.get_aluno_info(login); self.aluno_logado=aluno
        if not aluno: # Caso o login não corresponda a nenhum cadastro de aluno
            ttk.Label(main_frame,text="Cadastro não encontrado.",font=('Arial',12)).pack(); ttk.Button(main_frame,text="Sair",command=self.logout,style='Danger.TButton').pack(pady=10); return
        info=f"👤 {aluno.get('nome')} | ID: {aluno.get('id')} | Turma: {aluno.get('id_turma')}"
        ttk.Label(main_frame,text=info,font=('Arial',12,'italic')).pack(pady=10)
        # Botões de Ação do Aluno
        btn_container=ttk.Frame(main_frame,padding=10); btn_container.pack(pady=20)
        ttk.Button(btn_container,text="Consultar Cadastro",command=lambda:self.consultar_cadastro(aluno),style='Primary.TButton').pack(side="left",padx=10,pady=10,ipady=5)
        ttk.Button(btn_container,text="Ver Atividades Pendentes",command=lambda:self.ver_atividades(aluno),style='Primary.TButton').pack(side="left",padx=10,pady=10,ipady=5)
        ttk.Button(btn_container,text="Enviar Atividade",command=lambda:self.enviar_atividade_dialog(aluno),style='Success.TButton').pack(side="left",padx=10,pady=10,ipady=5)
        ttk.Button(btn_container,text="Ver Notas",command=lambda:self.ver_notas(aluno),style='Primary.TButton').pack(side="left",padx=10,pady=10,ipady=5)
        ttk.Separator(main_frame,orient='horizontal').pack(fill='x',pady=20,padx=50)
        ttk.Button(main_frame,text="Sair",command=self.logout,style='Danger.TButton').pack(pady=10,ipadx=20)

    def consultar_cadastro(self,aluno):
        """Exibe os dados cadastrais do aluno em um messagebox."""
        messagebox.showinfo("Cadastro do Aluno",f"ID: {aluno.get('id')}\nNome: {aluno.get('nome')}\nEmail: {aluno.get('email')}\nTurma: {aluno.get('id_turma')}")

    def ver_atividades(self,aluno):
        """Exibe uma lista de atividades que pertencem à turma do aluno e que ele AINDA NÃO entregou."""
        top=tk.Toplevel(self.root); top.title("Atividades Pendentes"); top.geometry("750x380")
        main_frame=ttk.Frame(top,padding="15",style='Content.TFrame'); main_frame.pack(fill="both",expand=True)
        ttk.Label(main_frame,text=f"Atividades Pendentes - Turma {aluno.get('id_turma')}",font=("Arial",14,"bold")).pack(pady=10)
        turma_id,aluno_id=aluno.get("id_turma"),aluno.get("id"); entregues_ids=get_entregues_ids(aluno_id)
        # Filtra: Atividades da turma E ID da atividade NÃO está nas entregues
        ativs=[a for a in ler_csv(ARQ_ATIV) if a.get("id_turma")==turma_id and a.get("id_atividade") not in entregues_ids]
        if not ativs: ttk.Label(main_frame,text="🎉 Nenhuma atividade pendente para sua turma!").pack(pady=20); return
        # ... (Criação da Listbox para exibir as atividades) ...
        list_frame=ttk.Frame(main_frame); list_frame.pack(padx=10,pady=10,fill="both",expand=True)
        scrollbar=ttk.Scrollbar(list_frame,orient=tk.VERTICAL)
        box=tk.Listbox(list_frame,width=100,height=12,yscrollcommand=scrollbar.set,font=('Consolas',10))
        scrollbar.config(command=box.yview); scrollbar.pack(side=tk.RIGHT,fill=tk.Y); box.pack(side=tk.LEFT,fill="both",expand=True)
        for a in ativs: box.insert(tk.END,f"ID: {a.get('id_atividade')} | Disciplina: {a.get('disciplina'):<12} | Descrição: {a.get('descricao')} (Prof: {a.get('id_professor')})")
        ttk.Button(main_frame,text="Fechar",command=top.destroy,style='Primary.TButton').pack(pady=10)

    def enviar_atividade_dialog(self,aluno):
        """Abre a janela para envio de resposta de atividade pelo aluno."""
        top=tk.Toplevel(self.root); top.title("Enviar Atividade"); top.geometry("450x420")
        main_frame=ttk.Frame(top,padding="15",style='Content.TFrame'); main_frame.pack(fill="both",expand=True)
        ttk.Label(main_frame,text="Envio de Atividade",font=("Arial",14,"bold")).pack(pady=10)
        turma_id,aluno_id=aluno.get("id_turma"),aluno.get("id"); entregues_ids=get_entregues_ids(aluno_id)
        atividades_pendentes=[a for a in ler_csv(ARQ_ATIV) if a.get("id_turma")==turma_id and a.get("id_atividade") not in entregues_ids]
        # Permite reenviar se todas foram entregues (opcional)
        atividades=atividades_pendentes or ([a for a in ler_csv(ARQ_ATIV) if a.get("id_turma")==turma_id] if messagebox.askyesno("Aviso","Todas as atividades foram entregues. Deseja reenviar alguma?") else [])
        if not atividades: ttk.Label(main_frame,text="Nenhuma atividade pendente para envio.").pack(pady=20); return
        opcoes=[f"ID: {a.get('id_atividade')} - {a.get('disciplina')} - {a.get('descricao')[:30]}..." for a in atividades]
        ativ_map={op:a.get("id_atividade") for op,a in zip(opcoes,atividades)} # Mapeamento para obter ID da atividade
        
        # ... (Campos de seleção e resposta) ...
        ttk.Label(main_frame,text="Selecione a Atividade:",font=('Arial',10,'bold')).pack(anchor="w",pady=(5,0))
        combo_ativ=ttk.Combobox(main_frame,values=opcoes,width=50,state="readonly"); combo_ativ.pack(fill="x",pady=5)
        ttk.Label(main_frame,text="Insira sua Resposta:",font=('Arial',10,'bold')).pack(anchor="w",pady=(10,0))
        e_resposta=tk.Text(main_frame,width=50,height=8,padx=5,pady=5,relief=tk.FLAT,bd=2); e_resposta.pack(fill="both",expand=True,pady=5,padx=5)
        
        def salvar():
            """Função de callback para salvar a entrega da atividade."""
            ativ_sel=combo_ativ.get(); resposta=e_resposta.get("1.0",tk.END).strip()
            if not ativ_sel or not resposta: messagebox.showwarning("Aviso","Preencha todos os campos."); return
            
            ativ_id=ativ_map[ativ_sel]; nova={"id_atividade":ativ_id,"id_aluno":aluno_id,"nome_aluno":aluno.get("nome"),"data_entrega":time.strftime("%Y-%m-%d %H:%M:%S"),"resposta":resposta}
            entregas=ler_csv(ARQ_ENTREGA); ja_entregue=any(e.get("id_atividade")==ativ_id and e.get("id_aluno")==aluno_id for e in entregas)
            
            if ja_entregue: # Se já entregou, pede confirmação para substituir
                if not messagebox.askyesno("Aviso","Você já enviou esta. Deseja substituí-la?"): return
                entregas_filtradas=[e for e in entregas if not (e.get("id_atividade")==ativ_id and e.get("id_aluno")==aluno_id)]
                entregas_filtradas.append(nova); escrever_csv(ARQ_ENTREGA,ENTREGA_FIELDS,entregas_filtradas); messagebox.showinfo("Sucesso","Atividade atualizada!")
            else: # Primeira entrega
                append_csv(ARQ_ENTREGA,nova,ENTREGA_FIELDS); messagebox.showinfo("Sucesso","Atividade enviada!")
            
            top.destroy(); self.show_aluno(self.usuario["login"]) # Recarrega a tela do aluno

        ttk.Button(main_frame,text="Enviar Resposta",command=salvar,style='Success.TButton').pack(pady=15,fill="x",padx=5)

    def ver_notas(self,aluno):
        """Exibe o boletim do aluno, formatando as notas por disciplina e aplicando cores de status."""
        top=tk.Toplevel(self.root); top.title("Notas"); top.geometry("450x350")
        main_frame=ttk.Frame(top,padding="15",style='Content.TFrame'); main_frame.pack(fill="both",expand=True)
        ttk.Label(main_frame,text=f"Boletim - {aluno.get('nome')}",font=("Arial",16,"bold"),foreground='#007bff').pack(pady=10)
        
        # Mapeia as notas do aluno logado
        notas_aluno={n.get("disciplina"):n.get("nota") for n in ler_csv(ARQ_NOTA) if n.get("id_aluno")==aluno.get("id")}
        
        grid_frame=ttk.Frame(main_frame,padding=10); grid_frame.pack(pady=15,fill="x",padx=20)
        for i,disc in enumerate(DISCIPLINAS):
            nota=notas_aluno.get(disc,'N/A')
            # Lógica de cor da nota: Verde (>=7), Laranja (>=5), Vermelho (<5)
            cor_nota='green' if nota!='N/A' and float(nota)>=7 else 'orange' if nota!='N/A' and float(nota)>=5 else 'red' if nota!='N/A' else 'gray'
            ttk.Label(grid_frame,text=f"📚 {disc}:",font=('Arial',11,'bold')).grid(row=i,column=0,sticky='w',pady=4,padx=10)
            ttk.Label(grid_frame,text=f"{nota}",font=('Arial',11,'bold'),foreground=cor_nota).grid(row=i,column=1,sticky='e',pady=4,padx=10)
        grid_frame.columnconfigure(1,weight=1)
        ttk.Button(main_frame,text="Fechar",command=top.destroy,style='Primary.TButton').pack(pady=10,ipadx=10)

    # ==============================================================================
    # 5. ÁREA DO PROFESSOR
    # ==============================================================================
    def show_prof(self,login):
        """Constrói a interface principal para o Professor."""
        self.clear()
        main_frame=ttk.Frame(self.root,padding="20",style='Content.TFrame'); main_frame.pack(fill="both",expand=True)
        ttk.Label(main_frame,text="Área do Professor",style='Titre.TLabel').pack(pady=15)
        ttk.Label(main_frame,text=f"👨‍🏫 Professor: {login}",font=('Arial',11,'italic')).pack(anchor="w",padx=10,pady=(0,10))
        ttk.Label(main_frame,text="Atividades cadastradas:",font=('Arial',12,'bold')).pack(anchor="w",padx=10,pady=(10,5))
        
        # Listbox para mostrar as atividades cadastradas
        list_frame=ttk.Frame(main_frame); list_frame.pack(padx=10,fill="x",expand=False)
        scrollbar=ttk.Scrollbar(list_frame,orient=tk.VERTICAL)
        box=tk.Listbox(list_frame,width=90,height=10,yscrollcommand=scrollbar.set,font=('Consolas',9))
        scrollbar.config(command=box.yview); scrollbar.pack(side=tk.RIGHT,fill=tk.Y); box.pack(side=tk.LEFT,fill="x",expand=True)
        for a in ler_csv(ARQ_ATIV): box.insert(tk.END,f"ID: {a.get('id_atividade')} | {a.get('disciplina'):<12} | {a.get('descricao')[:40]}... (Turma {a.get('id_turma')})")
        
        # Botões de Ação do Professor
        btn_container=ttk.Frame(main_frame,padding=10); btn_container.pack(pady=10)
        ttk.Button(btn_container,text="➕ Criar atividade",command=lambda:self.criar_atividade(login),style='Success.TButton').pack(side="left",padx=5)
        ttk.Button(btn_container,text="🗑️ Excluir Atividade",command=lambda:self.excluir_atividade(box),style='Danger.TButton').pack(side="left",padx=5)
        ttk.Button(btn_container,text="📦 Ver Entregas",command=lambda:self.ver_entregas(login),style='Primary.TButton').pack(side="left",padx=5)
        ttk.Button(btn_container,text="💯 Atribuir Nota",command=self.atribuir_nota_dialog,style='Primary.TButton').pack(side="left",padx=5)
        ttk.Button(main_frame,text="Sair",command=self.logout,style='Danger.TButton').pack(pady=10,ipadx=20)

    def criar_atividade(self,login):
        """Abre o diálogo para o professor criar uma nova atividade e associá-la a uma turma."""
        turmas=ler_csv(ARQ_TURM)
        if not turmas: messagebox.showwarning("Aviso","Nenhuma turma cadastrada."); return
        top=tk.Toplevel(self.root); top.title("Criar Atividade"); top.geometry("420x340")
        main_frame=ttk.Frame(top,padding="15",style='Content.TFrame'); main_frame.pack(fill="both",expand=True)
        ttk.Label(main_frame,text="Nova Atividade",font=("Arial",14,"bold")).pack(pady=10)
        
        # Campos de Disciplina, Descrição e Seleção de Turma
        ttk.Label(main_frame,text="Disciplina:",font=('Arial',10,'bold')).pack(anchor="w",pady=(5,0))
        combo_disc=ttk.Combobox(main_frame,values=DISCIPLINAS,width=42,state="readonly"); combo_disc.pack(fill="x",pady=5)
        ttk.Label(main_frame,text="Descrição:",font=('Arial',10,'bold')).pack(anchor="w",pady=(5,0))
        e_desc=ttk.Entry(main_frame,width=45); e_desc.pack(fill="x",pady=5,ipady=4)
        turmas_opcoes=[f"{t['id_turma']} - {t['nome_turma']}" for t in turmas if t.get('id_turma')]
        turmas_dict={op:op.split(" - ")[0].strip() for op in turmas_opcoes}
        ttk.Label(main_frame,text="Selecione a Turma:",font=('Arial',10,'bold')).pack(anchor="w",pady=(5,0))
        combo_turma=ttk.Combobox(main_frame,values=turmas_opcoes,width=42,state="readonly"); combo_turma.pack(fill="x",pady=5)
        
        def salvar():
            """Função de callback para salvar a nova atividade no ARQ_ATIV."""
            disc,desc,sel=combo_disc.get().strip(),e_desc.get().strip(),combo_turma.get().strip()
            if not all([disc,desc,sel]): messagebox.showwarning("Aviso","Preencha todos os campos."); return
            tid=turmas_dict.get(sel); 
            if not tid: messagebox.showerror("Erro","Erro ao obter o ID da turma."); return
            
            # Gera o próximo ID sequencial para a atividade
            ativs=ler_csv(ARQ_ATIV); maxid=max([int(a.get("id_atividade",0)) for a in ativs] or [0])
            nova={"id_atividade":str(maxid+1),"disciplina":disc,"descricao":desc,"id_professor":login,"id_turma":tid}
            
            append_csv(ARQ_ATIV,nova,ATIV_FIELDS); messagebox.showinfo("Sucesso",f"Atividade de {disc} criada."); top.destroy(); self.show_prof(login)

        ttk.Button(main_frame,text="Salvar Atividade",command=salvar,style='Success.TButton').pack(pady=20,fill="x")

    def excluir_atividade(self,box):
        """Remove a atividade selecionada da listbox e reescreve o ARQ_ATIV."""
        sel=box.curselection(); 
        if not sel: messagebox.showwarning("Aviso","Selecione uma atividade."); return
        if not messagebox.askyesno("Confirmar","Tem certeza que deseja excluir esta atividade?"): return
        try: aid=box.get(sel[0]).split("ID: ")[1].split(" |")[0].strip()
        except IndexError: messagebox.showerror("Erro","ID não encontrado."); return
        
        # Filtra a lista, removendo o registro com o ID selecionado
        ativs=[a for a in ler_csv(ARQ_ATIV) if a.get("id_atividade")!=aid]
        escrever_csv(ARQ_ATIV,ATIV_FIELDS,ativs); messagebox.showinfo("Ok","Atividade excluída."); self.show_prof(self.usuario["login"])

    def ver_entregas(self,prof_login):
        """Exibe as entregas de atividades que foram criadas pelo professor logado."""
        top=tk.Toplevel(self.root); top.title("Entregas"); top.geometry("750x500")
        main_frame=ttk.Frame(top,padding="15",style='Content.TFrame'); main_frame.pack(fill="both",expand=True)
        ttk.Label(main_frame,text="Entregas Recebidas",font=("Arial",16,"bold")).pack(pady=10)
        
        # Filtra as atividades criadas pelo professor
        todas_ativs=ler_csv(ARQ_ATIV); ativ_map={a.get("id_atividade"):a for a in todas_ativs if a.get("id_professor")==prof_login}
        if not ativ_map: ttk.Label(main_frame,text="Você não tem atividades cadastradas.").pack(pady=10); return
        
        # Filtra as entregas para corresponder às atividades do professor
        entregas_filtradas=[e for e in ler_csv(ARQ_ENTREGA) if e.get("id_atividade") in ativ_map]
        if not entregas_filtradas: ttk.Label(main_frame,text="Nenhuma entrega recebida.").pack(pady=10); return
        
        # Listbox para exibir as entregas
        list_frame=ttk.Frame(main_frame); list_frame.pack(padx=10,pady=10,fill="both",expand=True)
        scrollbar=ttk.Scrollbar(list_frame,orient=tk.VERTICAL); box=tk.Listbox(list_frame,width=100,height=15,yscrollcommand=scrollbar.set,font=('Consolas',9))
        scrollbar.config(command=box.yview); scrollbar.pack(side=tk.RIGHT,fill=tk.Y); box.pack(side=tk.LEFT,fill="both",expand=True)
        for e in entregas_filtradas:
            ativ=ativ_map.get(e.get("id_atividade"),{}); disc=ativ.get("disciplina","N/A"); desc=ativ.get("descricao","N/A")[:20]+"..."
            box.insert(tk.END,f"Aluno: {e.get('nome_aluno'):<20} | Atividade ID: {e.get('id_atividade'):<3} | Disciplina: {disc:<12} | Data: {e.get('data_entrega')}")
        
        def ver_resposta():
            """Abre uma nova janela para mostrar o texto completo da resposta do aluno."""
            sel=box.curselection(); 
            if not sel: messagebox.showwarning("Aviso","Selecione uma entrega."); return
            entrega=entregas_filtradas[sel[0]]; ativ=ativ_map.get(entrega.get("id_atividade"),{})
            detalhe=tk.Toplevel(top); detalhe.title(f"Resposta de {entrega.get('nome_aluno')}"); detalhe.geometry("600x400")
            det_frame=ttk.Frame(detalhe,padding="15",style='Content.TFrame'); det_frame.pack(fill="both",expand=True)
            # ... (Exibição da resposta em um widget Text desabilitado) ...
            ttk.Label(det_frame,text="Detalhes da Entrega",font=("Arial",14,"bold")).pack(pady=5)
            ttk.Label(det_frame,text=f"Aluno: {entrega.get('nome_aluno')} | Disciplina: {ativ.get('disciplina','N/A')}").pack(anchor="w",padx=10,pady=5)
            ttk.Label(det_frame,text="Resposta do Aluno:",font=("Arial",10,"bold")).pack(anchor="w",padx=10)
            t_resposta=tk.Text(det_frame,wrap="word",width=70,height=15,padx=5,pady=5,relief=tk.FLAT,bd=2); t_resposta.insert(tk.END,entrega.get("resposta"))
            t_resposta.config(state="disabled"); t_resposta.pack(padx=10,pady=5,fill="both",expand=True)
            ttk.Button(det_frame,text="Fechar",command=detalhe.destroy,style='Primary.TButton').pack(pady=10)

        btn_frame=ttk.Frame(main_frame); btn_frame.pack(pady=10)
        ttk.Button(btn_frame,text="Ver Resposta Completa",command=ver_resposta,style='Primary.TButton').pack(side="left",padx=10)
        ttk.Button(btn_frame,text="Fechar",command=top.destroy,style='Danger.TButton').pack(side="left",padx=10)

    def atribuir_nota_dialog(self):
        """Abre o diálogo para o professor selecionar um aluno/disciplina e atribuir uma nota."""
        alunos=ler_csv(ARQ_ALUN); 
        if not alunos: messagebox.showwarning("Aviso","Nenhum aluno cadastrado."); return
        top=tk.Toplevel(self.root); top.title("Atribuir Nota"); top.geometry("400x320")
        main_frame=ttk.Frame(top,padding="15",style='Content.TFrame'); main_frame.pack(fill="both",expand=True)
        ttk.Label(main_frame,text="Atribuir Nota ao Aluno",font=("Arial",14,"bold")).pack(pady=10)
        
        # Campos de seleção de Aluno, Disciplina e Nota
        ttk.Label(main_frame,text="Aluno:",font=('Arial',10,'bold')).pack(anchor="w",pady=(5,0))
        combo_aluno=ttk.Combobox(main_frame,values=[f"{a['id']} - {a['nome']}" for a in alunos],state="readonly"); combo_aluno.pack(fill="x",pady=5)
        ttk.Label(main_frame,text="Disciplina:",font=('Arial',10,'bold')).pack(anchor="w",pady=(5,0))
        combo_disc=ttk.Combobox(main_frame,values=DISCIPLINAS,state="readonly"); combo_disc.pack(fill="x",pady=5)
        ttk.Label(main_frame,text="Nota (0-10):",font=('Arial',10,'bold')).pack(anchor="w",pady=(5,0))
        e_nota=ttk.Entry(main_frame); e_nota.pack(fill="x",pady=5,ipady=4)
        
        def salvar_nota():
            """Função de callback para salvar ou atualizar a nota no ARQ_NOTA."""
            aluno_sel,disc,nota_str=combo_aluno.get(),combo_disc.get(),e_nota.get().strip()
            if not all([aluno_sel,disc,nota_str]): messagebox.showwarning("Aviso","Preencha todos os campos."); return
            try: nota=float(nota_str); assert 0<=nota<=10 # Validação de nota entre 0 e 10
            except: messagebox.showerror("Erro","Nota inválida."); return
            
            id_aluno=aluno_sel.split(" - ")[0]; notas=ler_csv(ARQ_NOTA); atualizadas=False
            
            # Tenta atualizar a nota se o registro já existir
            for n in notas:
                if n["id_aluno"]==id_aluno and n["disciplina"]==disc: n["nota"]=str(nota); atualizadas=True; break
            
            # Se não existir, adiciona um novo registro
            if not atualizadas: notas.append({"id_aluno":id_aluno,"disciplina":disc,"nota":str(nota)})
            
            escrever_csv(ARQ_NOTA,["id_aluno","disciplina","nota"],notas); messagebox.showinfo("Sucesso","Nota registrada."); top.destroy()

        ttk.Button(main_frame,text="Salvar Nota",command=salvar_nota,style='Success.TButton').pack(pady=15,fill="x")

    # ==============================================================================
    # 6. ÁREA DO COORDENADOR & ADMINISTRADOR (CRUD e Relatórios)
    # ==============================================================================
    def show_coord(self,login):
        """Constrói a interface principal para o Coordenador (foco em CRUD de Alunos/Turmas)."""
        self.clear()
        main_frame=ttk.Frame(self.root,padding="20",style='Content.TFrame'); main_frame.pack(fill="both",expand=True)
        ttk.Label(main_frame,text="Área do Coordenador",style='Titre.TLabel').pack(pady=15)
        ttk.Label(main_frame,text=f"Coordenador: {login}",font=('Arial',11,'italic')).pack(pady=10)
        
        btn_frame=ttk.Frame(main_frame,padding=10); btn_frame.pack(pady=20)
        # Botões de Ação CRUD
        ttk.Button(btn_frame,text="👀 Ver Alunos",command=lambda:self.lista_itens(ARQ_ALUN,"Alunos",lambda r:f"ID:{r.get('id')} - {r.get('nome')} | Turma: {r.get('id_turma')}"),style='Primary.TButton').grid(row=0,column=0,padx=15,pady=10,sticky="ew",ipady=5)
        ttk.Button(btn_frame,text="👀 Ver Turmas",command=lambda:self.lista_itens(ARQ_TURM,"Turmas",lambda r:f"ID:{r.get('id_turma')} - {r.get('nome_turma')}"),style='Primary.TButton').grid(row=0,column=1,padx=15,pady=10,sticky="ew",ipady=5)
        ttk.Button(btn_frame,text="➕ Criar Novo Aluno",command=self.criar_aluno,style='Success.TButton').grid(row=1,column=0,padx=15,pady=10,sticky="ew",ipady=5)
        ttk.Button(btn_frame,text="➕ Criar Nova Turma",command=self.criar_turma,style='Success.TButton').grid(row=1,column=1,padx=15,pady=10,sticky="ew",ipady=5)
        btn_frame.grid_columnconfigure(0,weight=1); btn_frame.grid_columnconfigure(1,weight=1)
        ttk.Button(main_frame,text="Sair",command=self.logout,style='Danger.TButton').pack(pady=30,ipadx=20)

    def show_adm(self,login):
        """Constrói a interface principal para o Administrador (CRUD Avançado e Gráficos)."""
        self.clear(); self.root.geometry("850x580") 
        main_frame=ttk.Frame(self.root,padding="20",style='Content.TFrame'); main_frame.pack(fill="both",expand=True)
        ttk.Label(main_frame,text="Área Administrativa",style='Titre.TLabel').pack(pady=15)
        
        # Notebook (Abas) para organizar CRUD e Gráficos
        notebook=ttk.Notebook(main_frame); notebook.pack(pady=10,padx=10,fill="both",expand=True)
        
        # ABA 1: Manutenção/CRUD
        f_ger=ttk.Frame(notebook,padding="15",style='Content.TFrame'); notebook.add(f_ger,text='⚙️ Manutenção/CRUD')
        ttk.Label(f_ger,text="👥 Gerenciamento de Alunos & Turmas",font=("Arial",12,"bold"),foreground='#007bff').pack(anchor="w",pady=(5,10))
        btnf1=ttk.Frame(f_ger); btnf1.pack(fill="x",pady=5)
        ttk.Button(btnf1,text="Ver Alunos",command=lambda:self.lista_itens(ARQ_ALUN,"Alunos",lambda r:f"ID:{r.get('id')} - {r.get('nome')} ({r.get('id_turma')})"),style='Primary.TButton').pack(side="left",padx=5,ipady=5)
        ttk.Button(btnf1,text="Criar Aluno",command=self.criar_aluno,style='Success.TButton').pack(side="left",padx=5,ipady=5)
        ttk.Button(btnf1,text="Ver Turmas",command=lambda:self.lista_itens(ARQ_TURM,"Turmas",lambda r:f"ID:{r.get('id_turma')} - {r.get('nome_turma')}"),style='Primary.TButton').pack(side="left",padx=5,ipady=5)
        ttk.Button(btnf1,text="Criar Turma",command=self.criar_turma,style='Success.TButton').pack(side="left",padx=5,ipady=5)
        ttk.Separator(f_ger,orient='horizontal').pack(fill='x',pady=20)
        ttk.Label(f_ger,text="👨‍🏫 Gerenciamento de Usuários & Atividades",font=("Arial",12,"bold"),foreground='#007bff').pack(anchor="w",pady=(5,10))
        btnf2=ttk.Frame(f_ger); btnf2.pack(fill="x",pady=5)
        ttk.Button(btnf2,text="Ver Usuários",command=lambda:self.lista_itens(ARQ_USU,"Usuários",lambda r:f"Login:{r.get('login')} - Tipo:{r.get('tipo')}"),style='Primary.TButton').pack(side="left",padx=5,ipady=5)
        ttk.Button(btnf2,text="Criar Usuário",command=self.criar_usuario_adm,style='Success.TButton').pack(side="left",padx=5,ipady=5)
        ttk.Button(btnf2,text="Ver Atividades",command=lambda:self.lista_itens(ARQ_ATIV,"Atividades",lambda r:f"ID:{r.get('id_atividade')} - {r.get('disciplina')} ({r.get('id_turma')})"),style='Primary.TButton').pack(side="left",padx=5,ipady=5)

        # ABA 2: Relatórios Gráficos
        f_graf=ttk.Frame(notebook,padding="15",style='Content.TFrame'); notebook.add(f_graf,text='📊 Relatórios Gráficos')
        ttk.Label(f_graf,text="Selecione o Relatório para Visualizar:",font=("Arial",12,"bold"),foreground='#007bff').pack(anchor="w",pady=(5,10))
        btnf3=ttk.Frame(f_graf); btnf3.pack(fill="x",pady=10)
        # Botões para geração dos Gráficos
        ttk.Button(btnf3,text="Alunos por Turma",command=lambda:self.mostrar_grafico("turma_aluno"),style='Primary.TButton').pack(side="left",padx=5,ipady=5)
        ttk.Button(btnf3,text="Média de Notas",command=lambda:self.mostrar_grafico("notas_disciplina"),style='Primary.TButton').pack(side="left",padx=5,ipady=5)
        ttk.Button(btnf3,text="Contagem de Atividades",command=lambda:self.mostrar_grafico("count_ativ"),style='Primary.TButton').pack(side="left",padx=5,ipady=5)
        
        ttk.Button(main_frame,text="Sair",command=self.logout,style='Danger.TButton').pack(pady=10,ipadx=20)

    def criar_usuario_adm(self):
        """Cria um novo usuário para o sistema (aluno, prof, adm, etc.) via simpledialogs."""
        login=simpledialog.askstring("Login","Login do novo usuário:"); 
        if not login: return
        senha=simpledialog.askstring("Senha","Senha do novo usuário:"); 
        if not senha: return
        tipos=["aluno","professor","coordenador","adm","tecnico"]
        tipo=simpledialog.askstring("Tipo","Tipo (aluno/professor/coordenador/adm/tecnico):").lower()
        if tipo not in tipos: messagebox.showerror("Erro","Tipo de usuário inválido."); return
        if any(u.get('login')==login for u in ler_csv(ARQ_USU)): messagebox.showerror("Erro","Login já existe."); return
        
        append_csv(ARQ_USU,{"login":login,"senha":senha,"tipo":tipo},["login","senha","tipo"]); messagebox.showinfo("Ok",f"Usuário '{login}' criado com sucesso.")

    def mostrar_grafico(self,tipo):
        """Processa os dados e desenha gráficos de barras no Canvas do Tkinter."""
        top=tk.Toplevel(self.root); top.title(f"Gráfico - {tipo.replace('_',' ').title()}"); top.geometry("650x450")
        main_frame=ttk.Frame(top,padding="15",style='Content.TFrame'); main_frame.pack(fill="both",expand=True)
        canvas=tk.Canvas(main_frame,width=620,height=300,bg="white",relief=tk.RIDGE,bd=2); canvas.pack(pady=10,padx=10)
        data,titulo={},""
        
        # 1. Processamento dos dados
        if tipo=="turma_aluno": # Contagem de alunos por turma
            titulo="Alunos por Turma"
            for a in ler_csv(ARQ_ALUN): data[a.get("id_turma","N/A")]=data.get(a.get("id_turma","N/A"),0)+1
        elif tipo=="notas_disciplina": # Cálculo da média de notas por disciplina
            titulo="Média de Notas por Disciplina"; temp,counts={},{}
            for n in ler_csv(ARQ_NOTA):
                disc,nota=n.get("disciplina"),float(n.get("nota",0))
                temp[disc]=temp.get(disc,0)+nota; counts[disc]=counts.get(disc,0)+1
            for disc in temp: data[disc]=temp[disc]/counts[disc]
        elif tipo=="count_ativ": # Contagem de atividades por disciplina
            titulo="Contagem de Atividades por Disciplina"
            for a in ler_csv(ARQ_ATIV): data[a.get("disciplina","N/A")]=data.get(a.get("disciplina","N/A"),0)+1
            
        ttk.Label(main_frame,text=titulo,font=("Arial",14,"bold"),foreground='#007bff').pack()
        categorias,valores=list(data.keys()),list(data.values())
        if not categorias: canvas.create_text(310,150,text="Dados insuficientes para o gráfico."); return
        
        # 2. Desenho do gráfico (lógica de Tkinter Canvas)
        max_val=max(valores) if valores else 1
        largura_barra,espaco,x_inicial,y_base,y_max=50,20,40,290,20
        for i,val in enumerate(valores):
            altura_norm=(val/max_val)*(y_base-y_max) # Normaliza a altura da barra
            x0=x_inicial+i*(largura_barra+espaco); x1=x0+largura_barra; y0=y_base-altura_norm; y1=y_base
            # Cor condicional (se for nota, usa cores de aprovação)
            cor="#4a7a8c" if tipo!="notas_disciplina" else "#28a745" if val>=7 else "#ffc107" if val>=5 else "#dc3545"
            canvas.create_rectangle(x0,y0,x1,y1,fill=cor,outline="#333")
            # Rótulos da Categoria e Valor
            label_text=categorias[i][:10]+("..." if len(categorias[i])>10 else "")
            canvas.create_text(x0+largura_barra/2,y_base+10,text=label_text,anchor="n",fill="black",font=('Arial',8))
            val_text=f"{val:.1f}" if tipo=="notas_disciplina" else str(int(val))
            canvas.create_text(x0+largura_barra/2,y0-5,text=val_text,anchor="s",fill="black",font=('Arial',8,'bold'))
        canvas.create_line(x_inicial-10,y_base,x_inicial+len(categorias)*(largura_barra+espaco)-espaco,y_base,fill="black") # Eixo X
        ttk.Button(main_frame,text="Fechar",command=top.destroy,style='Primary.TButton').pack(pady=10)

    def lista_itens(self,arq,titulo,format_func):
        """Abre uma janela pop-up genérica para listar o conteúdo de qualquer CSV, formatado por uma função."""
        top=tk.Toplevel(self.root); top.title(titulo); top.geometry("700x400")
        main_frame=ttk.Frame(top,padding="15",style='Content.TFrame'); main_frame.pack(fill="both",expand=True)
        ttk.Label(main_frame,text=f"Lista de {titulo}",font=("Arial",14,"bold")).pack(pady=10)
        rows=ler_csv(arq)
        if not rows: ttk.Label(main_frame,text=f"Nenhum(a) {titulo.lower()} cadastrado.",font=('Arial',11)).pack(pady=20)
        else:
            list_frame=ttk.Frame(main_frame); list_frame.pack(padx=10,pady=10,fill="both",expand=True)
            scrollbar=ttk.Scrollbar(list_frame,orient=tk.VERTICAL)
            box=tk.Listbox(list_frame,width=90,height=12,yscrollcommand=scrollbar.set,font=('Consolas',10),relief=tk.FLAT,bd=2)
            scrollbar.config(command=box.yview); scrollbar.pack(side=tk.RIGHT,fill=tk.Y); box.pack(side=tk.LEFT,fill="both",expand=True)
            for r in rows: box.insert(tk.END,format_func(r)) # Usa a função de formatação fornecida
        ttk.Button(main_frame,text="Fechar",command=top.destroy,style='Primary.TButton').pack(pady=10)

    def criar_aluno(self):
        """Coleta dados e insere um novo aluno no ARQ_ALUN, gerando um ID sequencial."""
        nome=simpledialog.askstring("Nome","Nome do aluno:"); 
        if not nome: return
        email=simpledialog.askstring("Email","Email:"); 
        if not email: return
        turmas=ler_csv(ARQ_TURM); 
        if not turmas: messagebox.showerror("Erro","Nenhuma turma cadastrada."); return
        opcoes=[f"{t['id_turma']} - {t['nome_turma']}" for t in turmas]
        escolha=simpledialog.askstring("Turma","Escolha a turma:\n"+"\n".join(opcoes)); 
        if not escolha: return
        
        # Gera o próximo ID sequencial
        id_turma=escolha.split("-")[0].strip(); alunos=ler_csv(ARQ_ALUN); maxid=max([int(a.get("id",0)) for a in alunos] or [0])
        
        append_csv(ARQ_ALUN,{"id":str(maxid+1),"nome":nome,"email":email,"id_turma":id_turma},ALUN_FIELDS); messagebox.showinfo("Ok","Aluno criado.")

    def criar_turma(self):
        """Coleta o nome e insere uma nova turma no ARQ_TURM, gerando um ID sequencial."""
        nome=simpledialog.askstring("Nome turma","Nome da turma:"); 
        if not nome: return
        turmas=ler_csv(ARQ_TURM); maxid=max([int(t.get("id_turma",0)) for t in turmas] or [0])
        append_csv(ARQ_TURM,{"id_turma":str(maxid+1),"nome_turma":nome},TURM_FIELDS); messagebox.showinfo("Ok","Turma criada.")

# ==============================================================================
# 7. MAIN LOOP
# ==============================================================================
if __name__=="__main__":
    """Ponto de entrada da aplicação."""
    os.makedirs(BASE,exist_ok=True); # Garante que o diretório de saída exista
    root=tk.Tk(); # Cria a janela principal
    App(root); # Inicializa a aplicação
    root.mainloop() # Inicia o loop de eventos do Tkinter
