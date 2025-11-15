// Funções de baixo nível e gestão de usuários em C.

/*
  SISTEMA ACADÊMICO — fluxo inicial de cadastro por perfil + login
  ----------------------------------------------------------------
  O que este programa faz:
    • Ao iniciar: menu de boas-vindas
        1) Criar nova conta (escolhe tipo: aluno/prof/coord/adm → cria e-mail/senha → salva em usuarios.csv)
        2) Já tenho conta (login por e-mail/senha)
    • Depois do login: menus por perfil com as funcionalidades:
        - Usuários (ADM e COORD): criar/listar usuários
        - Alunos: CAD/ALT/DEL/Listar
        - Turmas: criar, listar, matricular aluno
        - Atividades: professor cria/exclui e lista por turma
    • Persistência em CSV (legível no Bloco de Notas / consumido pelo Python):
        usuarios.csv   => tipo;login;senha
        alunos.csv     => id;nome;idade;email;curso;id_turma
        turmas.csv     => id_turma;nome_turma
        atividades.csv => id_atividade;descricao;id_professor;id_turma
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#ifdef _WIN32
  #define CLEAR() system("cls")
  #define PAUSE() do { printf("\nPressione ENTER para continuar..."); fflush(stdout); int c; while((c=getchar())!='\n'&&c!=EOF){} } while(0)
#else
  #define CLEAR() system("clear")
  #define PAUSE() do { printf("\nPressione ENTER para continuar..."); fflush(stdout); int c; while((c=getchar())!='\n'&&c!=EOF){} } while(0)
#endif

/* ======================== PARÂMETROS GERAIS ========================= */
#define MAX_STR      100
#define MAX_LINHA    512
#define MAX_ALUNOS   2000
#define MAX_TURMAS   300
#define MAX_ATIV     2000
#define MAX_USERS    200

/* ======================== ARQUIVOS (CSV) ============================ */
#define ARQ_USU   "usuarios.csv"
#define ARQ_ALU   "alunos.csv"
#define ARQ_TUR   "turmas.csv"
#define ARQ_ATV   "atividades.csv"

/* ======================== TIPOS DE DADO ============================= */
typedef struct {
  char tipo[16];       // "aluno", "prof", "coord", "adm"
  char login[MAX_STR]; // e-mail
  char senha[MAX_STR];
} Usuario;

typedef struct {
  int  id;
  char nome[MAX_STR];
  int  idade;
  char email[MAX_STR];
  char curso[MAX_STR];
  int  id_turma;      // -1 se não matriculado
} Aluno;

typedef struct {
  int  id_turma;
  char nome_turma[MAX_STR];
} Turma;

typedef struct {
  int  id_atividade;
  char descricao[MAX_STR];
  char id_professor[MAX_STR]; // login do prof (email)
  int  id_turma;
} Atividade;

/* ===================== VETORES (banco em memória) =================== */
Usuario   Vusuarios[MAX_USERS]; int Nusuarios = 0;
Aluno     Valunos  [MAX_ALUNOS]; int Nalunos   = 0; int prox_id_aluno = 1;
Turma     Vturmas  [MAX_TURMAS]; int Nturmas   = 0; int prox_id_turma = 1;
Atividade Vativ    [MAX_ATIV  ]; int Nativ     = 0; int prox_id_ativ  = 1;

/* ======================== PROTÓTIPOS (evita erros) ================== */
void ler_linha(const char *prompt, char *dst, size_t tam);
int  ler_int(const char *prompt);
int  confirma(const char *q);
int  arquivo_existe(const char *path);
char* next_tok(char *ctx);
int  existe_login(const char *login);
int  email_valido(const char *e);

void salvar_usuarios(void);
void carregar_usuarios(void);
void salvar_alunos(void);
void carregar_alunos(void);
void salvar_turmas(void);
void carregar_turmas(void);
void salvar_atividades(void);
void carregar_atividades(void);

int  idx_aluno_por_id(int id);
int  idx_turma_por_id(int id);

void usuarios_listar(void);
void escolher_tipo_usuario(char *tipo_out, size_t tam);
void usuarios_criar_fluxo_escolha(void);       // <- usada no main
void alunos_listar(void);
void alunos_cadastrar(void);
void alunos_atualizar(void);
void alunos_remover(void);
void turmas_listar(void);
void turmas_criar(void);
void turmas_matricular_aluno(void);
void atividades_listar_por_turma(int id_turma);
void atividades_criar(const char *login_prof);
void atividades_excluir(void);

typedef struct {
  int  autenticado;        // 0/1
  char tipo[16];           // "aluno", "prof", "coord", "adm"
  char login[MAX_STR];     // e-mail
} Sessao;

Sessao login(void);

void menu_usuarios(void);
void menu_aluno(const Sessao *s);
void menu_prof(const Sessao *s);
void menu_coord(const Sessao *s);
void menu_adm(const Sessao *s);

void tela_boas_vindas(void);
void carregar_tudo(void);

/* ======================== IMPLEMENTAÇÕES ============================ */
void ler_linha(const char *prompt, char *dst, size_t tam) {
  if (prompt && *prompt) { printf("%s", prompt); fflush(stdout); }
  if (fgets(dst, (int)tam, stdin)) {
    size_t n = strlen(dst);
    if (n>0 && dst[n-1]=='\n') dst[n-1]='\0';
  } else { dst[0]='\0'; clearerr(stdin); }
}

int ler_int(const char *prompt) { char b[64]; ler_linha(prompt, b, sizeof(b)); return atoi(b); }
int confirma(const char *q) { char r[8]; ler_linha(q, r, sizeof(r)); return (r[0]=='s'||r[0]=='S'); }

int arquivo_existe(const char *path) { FILE *f=fopen(path,"r"); if(!f) return 0; fclose(f); return 1; }
char* next_tok(char *ctx) { return strtok(ctx, ";\r\n"); }

int existe_login(const char *login) {
  for (int i=0;i<Nusuarios;i++) if (!strcmp(Vusuarios[i].login, login)) return 1;
  return 0;
}
int email_valido(const char *e) {
  return (strchr(e,'@') && strchr(e,'.'));
}

/* ======================== PERSISTÊNCIA: USUÁRIOS ===================== */
void salvar_usuarios() {
  FILE *f = fopen(ARQ_USU, "w");
  if (!f) { perror("usuarios.csv"); return; }
  fprintf(f, "tipo;login;senha\n");
  for (int i=0;i<Nusuarios;i++)
    fprintf(f, "%s;%s;%s\n", Vusuarios[i].tipo, Vusuarios[i].login, Vusuarios[i].senha);
  fclose(f);
}

void carregar_usuarios() {
  Nusuarios = 0;
  if (!arquivo_existe(ARQ_USU)) {
    // base didática inicial (facilita primeiro acesso)
    strcpy(Vusuarios[0].tipo,"adm");   strcpy(Vusuarios[0].login,"admin@pim.com");  strcpy(Vusuarios[0].senha,"master");
    strcpy(Vusuarios[1].tipo,"coord"); strcpy(Vusuarios[1].login,"coord1@pim.com"); strcpy(Vusuarios[1].senha,"123");
    strcpy(Vusuarios[2].tipo,"prof");  strcpy(Vusuarios[2].login,"prof1@pim.com");  strcpy(Vusuarios[2].senha,"123");
    strcpy(Vusuarios[3].tipo,"aluno"); strcpy(Vusuarios[3].login,"aluno1@pim.com"); strcpy(Vusuarios[3].senha,"123");
    Nusuarios = 4;
    salvar_usuarios();
    return;
  }
  FILE *f = fopen(ARQ_USU, "r"); if (!f) return;
  char linha[MAX_LINHA];
  fgets(linha, sizeof(linha), f);
  while (fgets(linha, sizeof(linha), f) && Nusuarios < MAX_USERS) {
    char *p = next_tok(linha); if (!p) continue; strncpy(Vusuarios[Nusuarios].tipo, p, sizeof(Vusuarios[Nusuarios].tipo));
    p = next_tok(NULL); if (!p) continue; strncpy(Vusuarios[Nusuarios].login,p, sizeof(Vusuarios[Nusuarios].login));
    p = next_tok(NULL); if (!p) continue; strncpy(Vusuarios[Nusuarios].senha,p, sizeof(Vusuarios[Nusuarios].senha));
    Nusuarios++;
  }
  fclose(f);
}

/* ======================== PERSISTÊNCIA: ALUNOS ======================= */
void salvar_alunos() {
  FILE *f = fopen(ARQ_ALU, "w");
  if (!f) { perror("alunos.csv"); return; }
  fprintf(f, "id;nome;idade;email;curso;id_turma\n");
  for (int i=0;i<Nalunos;i++)
    fprintf(f,"%d;%s;%d;%s;%s;%d\n", Valunos[i].id, Valunos[i].nome, Valunos[i].idade,
            Valunos[i].email, Valunos[i].curso, Valunos[i].id_turma);
  fclose(f);
}

void carregar_alunos() {
  Nalunos = 0; prox_id_aluno = 1;
  if (!arquivo_existe(ARQ_ALU)) { salvar_alunos(); return; }
  FILE *f = fopen(ARQ_ALU,"r"); if(!f) return;
  char linha[MAX_LINHA];
  fgets(linha,sizeof(linha),f);
  while (fgets(linha,sizeof(linha),f) && Nalunos<MAX_ALUNOS) {
    char *p = next_tok(linha); if(!p) continue; Valunos[Nalunos].id = atoi(p);
    p = next_tok(NULL); if(!p) continue; strncpy(Valunos[Nalunos].nome,p,sizeof(Valunos[Nalunos].nome));
    p = next_tok(NULL); if(!p) continue; Valunos[Nalunos].idade = atoi(p);
    p = next_tok(NULL); if(!p) continue; strncpy(Valunos[Nalunos].email,p,sizeof(Valunos[Nalunos].email));
    p = next_tok(NULL); if(!p) continue; strncpy(Valunos[Nalunos].curso,p,sizeof(Valunos[Nalunos].curso));
    p = next_tok(NULL); if(!p) continue; Valunos[Nalunos].id_turma = atoi(p);
    if (Valunos[Nalunos].id >= prox_id_aluno) prox_id_aluno = Valunos[Nalunos].id + 1;
    Nalunos++;
  }
  fclose(f);
}

/* ======================== PERSISTÊNCIA: TURMAS ======================= */
void salvar_turmas() {
  FILE *f = fopen(ARQ_TUR, "w");
  if (!f) { perror("turmas.csv"); return; }
  fprintf(f,"id_turma;nome_turma\n");
  for (int i=0;i<Nturmas;i++)
    fprintf(f,"%d;%s\n", Vturmas[i].id_turma, Vturmas[i].nome_turma);
  fclose(f);
}

void carregar_turmas() {
  Nturmas = 0; prox_id_turma = 1;
  if (!arquivo_existe(ARQ_TUR)) { salvar_turmas(); return; }
  FILE *f = fopen(ARQ_TUR,"r"); if(!f) return;
  char linha[MAX_LINHA];
  fgets(linha,sizeof(linha),f);
  while (fgets(linha,sizeof(linha),f) && Nturmas<MAX_TURMAS) {
    char *p = next_tok(linha); if(!p) continue; Vturmas[Nturmas].id_turma = atoi(p);
    p = next_tok(NULL); if(!p) continue; strncpy(Vturmas[Nturmas].nome_turma,p,sizeof(Vturmas[Nturmas].nome_turma));
    if (Vturmas[Nturmas].id_turma >= prox_id_turma) prox_id_turma = Vturmas[Nturmas].id_turma + 1;
    Nturmas++;
  }
  fclose(f);
}

/* ======================== PERSISTÊNCIA: ATIVIDADES =================== */
void salvar_atividades() {
  FILE *f = fopen(ARQ_ATV, "w");
  if (!f) { perror("atividades.csv"); return; }
  fprintf(f,"id_atividade;descricao;id_professor;id_turma\n");
  for (int i=0;i<Nativ;i++)
    fprintf(f,"%d;%s;%s;%d\n", Vativ[i].id_atividade, Vativ[i].descricao, Vativ[i].id_professor, Vativ[i].id_turma);
  fclose(f);
}

void carregar_atividades() {
  Nativ = 0; prox_id_ativ = 1;
  if (!arquivo_existe(ARQ_ATV)) { salvar_atividades(); return; }
  FILE *f = fopen(ARQ_ATV,"r"); if(!f) return;
  char linha[MAX_LINHA];
  fgets(linha,sizeof(linha),f);
  while (fgets(linha,sizeof(linha),f) && Nativ<MAX_ATIV) {
    char *p = next_tok(linha); if(!p) continue; Vativ[Nativ].id_atividade = atoi(p);
    p = next_tok(NULL); if(!p) continue; strncpy(Vativ[Nativ].descricao,p,sizeof(Vativ[Nativ].descricao));
    p = next_tok(NULL); if(!p) continue; strncpy(Vativ[Nativ].id_professor,p,sizeof(Vativ[Nativ].id_professor));
    p = next_tok(NULL); if(!p) continue; Vativ[Nativ].id_turma = atoi(p);
    if (Vativ[Nativ].id_atividade >= prox_id_ativ) prox_id_ativ = Vativ[Nativ].id_atividade + 1;
    Nativ++;
  }
  fclose(f);
}

/* ======================== BUSCAS AUXILIARES ========================= */
int idx_aluno_por_id(int id) { for(int i=0;i<Nalunos;i++) if(Valunos[i].id==id) return i; return -1; }
int idx_turma_por_id(int id) { for(int i=0;i<Nturmas;i++) if(Vturmas[i].id_turma==id) return i; return -1; }

/* ======================== MÓDULO: USUÁRIOS ========================== */
void usuarios_listar() {
  if (Nusuarios==0) { puts("Nenhum usuario."); return; }
  printf("\n%-8s | %-26s | %-12s\n","TIPO","LOGIN (email)","SENHA");
  printf("-----------------------------------------------\n");
  for (int i=0;i<Nusuarios;i++)
    printf("%-8s | %-26s | %-12s\n", Vusuarios[i].tipo, Vusuarios[i].login, Vusuarios[i].senha);
}

void escolher_tipo_usuario(char *tipo_out, size_t tam) {
  puts("\nSelecione seu perfil:");
  puts("  1) aluno");
  puts("  2) professor");
  puts("  3) coordenador");
  puts("  4) adm");
  int op = ler_int("Escolha: ");
  switch(op) {
    case 1: strncpy(tipo_out,"aluno",tam); break;
    case 2: strncpy(tipo_out,"prof",tam);  break;
    case 3: strncpy(tipo_out,"coord",tam); break;
    case 4: strncpy(tipo_out,"adm",tam);   break;
    default: puts("Opcao invalida. Padrao: aluno."); strncpy(tipo_out,"aluno",tam); break;
  }
}

/* fluxo inicial: usuario escolhe tipo, cria email/senha e salva em CSV */
void usuarios_criar_fluxo_escolha() {
  if (Nusuarios >= MAX_USERS) { puts("Limite de usuarios atingido."); return; }

  puts("\n=== CRIAR NOVA CONTA ===");
  Usuario u; u.tipo[0]=u.login[0]=u.senha[0]='\0';
  escolher_tipo_usuario(u.tipo, sizeof(u.tipo));

  // login = e-mail
  while (1) {
    printf("Crie seu login (email): ");
    fflush(stdout);
    ler_linha("", u.login, sizeof(u.login));
    if (!strlen(u.login)) { puts("Email nao pode ser vazio.\n"); continue; }
    if (!email_valido(u.login)) { puts("Formato de email invalido.\n"); u.login[0]='\0'; continue; }
    if (existe_login(u.login)) { puts("Ja existe este email. Tente outro.\n"); u.login[0]='\0'; continue; }
    break;
  }

  // senha
  char confirma_senha[MAX_STR];
  while (1) {
    printf("Crie sua senha: ");
    fflush(stdout);
    ler_linha("", u.senha, sizeof(u.senha));
    printf("Confirme a senha: ");
    fflush(stdout);
    ler_linha("", confirma_senha, sizeof(confirma_senha));
    if (strcmp(u.senha, confirma_senha)!=0) {
      puts("As senhas nao conferem. Tente novamente.\n");
      u.senha[0]='\0';
      continue;
    }
    if (!strlen(u.senha)) { puts("Senha nao pode ser vazia.\n"); continue; }
    break;
  }

  Vusuarios[Nusuarios++] = u;
  salvar_usuarios();

  puts("\nConta criada com sucesso!");
  printf("Perfil: %s | Email: %s\n", u.tipo, u.login);
  puts("Agora selecione '2) Ja tenho conta' no menu para fazer login.");
}

/* ======================== MÓDULO: ALUNOS ============================ */
void alunos_listar() {
  if (Nalunos==0) { puts("Nenhum aluno."); return; }
  printf("\n%-4s | %-28s | %-5s | %-28s | %-12s | %-7s\n",
         "ID","NOME","IDADE","EMAIL","CURSO","TURMA");
  printf("-----------------------------------------------------------------------------------------------\n");
  for (int i=0;i<Nalunos;i++)
    printf("%-4d | %-28s | %-5d | %-28s | %-12s | %-7d\n",
        Valunos[i].id, Valunos[i].nome, Valunos[i].idade,
        Valunos[i].email, Valunos[i].curso, Valunos[i].id_turma);
}

void alunos_cadastrar() {
  if (Nalunos>=MAX_ALUNOS) { puts("Limite de alunos atingido."); return; }
  Aluno a;
  a.id = prox_id_aluno++;
  ler_linha("Nome: ", a.nome, sizeof(a.nome));
  a.idade = ler_int("Idade: ");
  ler_linha("Email: ", a.email, sizeof(a.email));
  ler_linha("Curso: ", a.curso, sizeof(a.curso));
  a.id_turma = -1;
  Valunos[Nalunos++] = a;
  salvar_alunos();
  printf("Aluno ID %d cadastrado!\n", a.id);
}

void alunos_atualizar() {
  int id = ler_int("ID do aluno: ");
  int i = idx_aluno_por_id(id);
  if (i<0) { puts("ID nao encontrado."); return; }

  char b[MAX_STR];
  printf("Nome atual: %s\n", Valunos[i].nome);
  ler_linha("Novo nome (ENTER p/ manter): ", b, sizeof(b)); if(strlen(b)) strncpy(Valunos[i].nome,b,sizeof(Valunos[i].nome));

  printf("Idade atual: %d\n", Valunos[i].idade);
  ler_linha("Nova idade (ENTER p/ manter): ", b, sizeof(b)); if(strlen(b)) Valunos[i].idade = atoi(b);

  printf("Email atual: %s\n", Valunos[i].email);
  ler_linha("Novo email (ENTER p/ manter): ", b, sizeof(b)); if(strlen(b)) strncpy(Valunos[i].email,b,sizeof(Valunos[i].email));

  printf("Curso atual: %s\n", Valunos[i].curso);
  ler_linha("Novo curso (ENTER p/ manter): ", b, sizeof(b)); if(strlen(b)) strncpy(Valunos[i].curso,b,sizeof(Valunos[i].curso));

  salvar_alunos(); puts("Atualizado!");
}

void alunos_remover() {
  int id = ler_int("ID do aluno para remover: ");
  int i = idx_aluno_por_id(id);
  if (i<0) { puts("ID nao encontrado."); return; }
  if (!confirma("Confirma remocao? (s/N): ")) return;
  for (int k=i;k<Nalunos-1;k++) Valunos[k]=Valunos[k+1];
  Nalunos--; salvar_alunos(); puts("Removido.");
}

/* ======================== MÓDULO: TURMAS ============================ */
void turmas_listar() {
  if (Nturmas==0) { puts("Nenhuma turma."); return; }
  printf("\n%-7s | %-20s\n","ID","NOME TURMA");
  printf("---------------------------\n");
  for (int i=0;i<Nturmas;i++)
    printf("%-7d | %-20s\n", Vturmas[i].id_turma, Vturmas[i].nome_turma);
}

void turmas_criar() {
  if (Nturmas>=MAX_TURMAS) { puts("Limite de turmas atingido."); return; }
  Turma t; t.id_turma = prox_id_turma++;
  ler_linha("Nome da turma: ", t.nome_turma, sizeof(t.nome_turma));
  Vturmas[Nturmas++] = t;
  salvar_turmas();
  printf("Turma %d criada!\n", t.id_turma);
}

void turmas_matricular_aluno() {
  int id_al = ler_int("ID do aluno: ");
  int ia = idx_aluno_por_id(id_al);
  if (ia<0) { puts("Aluno nao encontrado."); return; }
  turmas_listar();
  int id_t = ler_int("ID da turma: ");
  int it = idx_turma_por_id(id_t);
  if (it<0) { puts("Turma nao encontrada."); return; }
  Valunos[ia].id_turma = id_t;
  salvar_alunos();
  printf("Aluno %d matriculado na turma %d.\n", id_al, id_t);
}

/* ======================== MÓDULO: ATIVIDADES ======================== */
void atividades_listar_por_turma(int id_turma) {
  printf("\nATIVIDADES da Turma %d\n", id_turma);
  for (int i=0;i<Nativ;i++)
    if (Vativ[i].id_turma==id_turma)
      printf(" - [%d] %s (prof: %s)\n", Vativ[i].id_atividade, Vativ[i].descricao, Vativ[i].id_professor);
}

void atividades_criar(const char *login_prof) {
  if (Nativ>=MAX_ATIV) { puts("Limite de atividades atingido."); return; }
  Atividade a; a.id_atividade = prox_id_ativ++;
  ler_linha("Descricao da atividade: ", a.descricao, sizeof(a.descricao));
  strncpy(a.id_professor, login_prof, sizeof(a.id_professor));
  turmas_listar();
  a.id_turma = ler_int("ID da turma: ");
  if (idx_turma_por_id(a.id_turma)<0) { puts("Turma invalida."); return; }
  Vativ[Nativ++] = a; salvar_atividades(); puts("Atividade criada!");
}

void atividades_excluir() {
  int id = ler_int("ID da atividade: ");
  int pos=-1; for(int i=0;i<Nativ;i++) if(Vativ[i].id_atividade==id){pos=i;break;}
  if (pos<0) { puts("Atividade nao encontrada."); return; }
  if (!confirma("Confirma exclusao? (s/N): ")) return;
  for (int k=pos;k<Nativ-1;k++) Vativ[k]=Vativ[k+1];
  Nativ--; salvar_atividades(); puts("Excluida.");
}

/* ======================== LOGIN / PERMISSÕES ======================== */
/* ======================== LOGIN / PERMISSÕES ======================== */
Sessao login() {
  Sessao s = {0,"",""};
  char l[MAX_STR], p[MAX_STR];
  char tipoEscolhido[16] = "";

  CLEAR();
  puts("=== LOGIN ===");
  // 1) Primeiro o usuário escolhe o perfil:
  escolher_tipo_usuario(tipoEscolhido, sizeof(tipoEscolhido)); // 1..4 -> preenche "aluno/prof/coord/adm"

  // 2) Depois digita email e senha:
  ler_linha("Email: ", l, sizeof(l));
  ler_linha("Senha: ", p, sizeof(p));

  // 3) Valida credenciais + TIPO correspondente
  for (int i=0;i<Nusuarios;i++) {
    if (!strcmp(Vusuarios[i].login, l) &&
        !strcmp(Vusuarios[i].senha, p) &&
        !strcmp(Vusuarios[i].tipo,  tipoEscolhido)) {
      s.autenticado = 1;
      strncpy(s.tipo,  Vusuarios[i].tipo,  sizeof(s.tipo));
      strncpy(s.login, Vusuarios[i].login, sizeof(s.login));
      return s;
    }
  }

  puts("\nCredenciais invalidas OU perfil selecionado nao corresponde a este usuario.");
  puts("Dica: verifique se selecionou o perfil certo (aluno/prof/coord/adm).");
  PAUSE();
  return s;
}

/* ======================== MENUS POR PERFIL ========================== */
void menu_usuarios() {
  for(;;){
    CLEAR();
    puts("=== GERENCIAR USUARIOS ===");
    puts("1) Criar usuario (escolher tipo)");
    puts("2) Listar usuarios");
    puts("0) Voltar");
    int op = ler_int("Opcao: ");
    if (op==0) return;
    if (op==1) { usuarios_criar_fluxo_escolha(); PAUSE(); }
    else if (op==2) { usuarios_listar(); PAUSE(); }
  }
}

void menu_aluno(const Sessao *s) {
  for(;;){
    CLEAR();
    puts("=== MENU ALUNO ===");
    puts("1) Ver minhas atividades (informando meu ID de aluno)");
    puts("0) Sair");
    int op = ler_int("Opcao: ");
    if (op==0) return;
    if (op==1) {
      int id_al = ler_int("Seu ID de aluno: ");
      int ia = idx_aluno_por_id(id_al);
      if (ia<0) { puts("Aluno nao encontrado."); PAUSE(); continue; }
      if (Valunos[ia].id_turma<0) { puts("Voce nao esta matriculado em turma."); PAUSE(); continue; }
      atividades_listar_por_turma(Valunos[ia].id_turma); PAUSE();
    }
  }
}

void menu_prof(const Sessao *s) {
  for(;;){
    CLEAR();
    puts("=== MENU PROFESSOR ===");
    puts("1) Criar atividade");
    puts("2) Excluir atividade");
    puts("3) Ver atividades de uma turma");
    puts("0) Sair");
    int op = ler_int("Opcao: ");
    if (op==0) return;
    if (op==1) { atividades_criar(s->login); PAUSE(); }
    else if (op==2) { atividades_excluir(); PAUSE(); }
    else if (op==3) { int t=ler_int("ID da turma: "); atividades_listar_por_turma(t); PAUSE(); }
  }
}

void menu_coord(const Sessao *s) {
  for(;;){
    CLEAR();
    puts("=== MENU COORDENADOR ===");
    puts("1) Gerenciar usuarios (criar/listar)");
    puts("2) Cadastrar aluno");
    puts("3) Listar alunos");
    puts("4) Atualizar aluno");
    puts("5) Remover aluno");
    puts("6) Criar turma");
    puts("7) Listar turmas");
    puts("8) Matricular aluno em turma");
    puts("0) Sair");
    int op = ler_int("Opcao: ");
    if (op==0) return;
    switch(op){
      case 1: menu_usuarios(); break;
      case 2: alunos_cadastrar(); break;
      case 3: alunos_listar(); break;
      case 4: alunos_atualizar(); break;
      case 5: alunos_remover(); break;
      case 6: turmas_criar(); break;
      case 7: turmas_listar(); break;
      case 8: turmas_matricular_aluno(); break;
      default: puts("Opcao invalida."); break;
    }
    PAUSE();
  }
}

void menu_adm(const Sessao *s) {
  for(;;){
    CLEAR();
    puts("=== MENU ADMINISTRADOR ===");
    puts("1) Gerenciar usuarios (criar/listar)");
    puts("2) (Atalho) Listar alunos");
    puts("0) Sair");
    int op = ler_int("Opcao: ");
    if (op==0) return;
    if (op==1) { menu_usuarios(); }
    else if (op==2) { alunos_listar(); PAUSE(); }
  }
}

/* ======================== HOME / INICIALIZAÇÃO ====================== */
void tela_boas_vindas() {
  puts("=====================================");
  puts("   SISTEMA ACADEMICO - PIM (C/CSV)   ");
  puts("=====================================");
}

void carregar_tudo() {
  carregar_usuarios();
  carregar_alunos();
  carregar_turmas();
  carregar_atividades();
}

int main(void) {
  carregar_tudo();

  // garante que todos os prompts apareçam no console
  setvbuf(stdout, NULL, _IONBF, 0);

  for (;;) {
    CLEAR();
    tela_boas_vindas();

    printf("\n1) Criar nova conta (perfil + email/senha)\n");
    printf("2) Ja tenho conta (login)\n");
    printf("0) Sair\n");

    int op = ler_int("Opcao: ");

    if (op == 0) {
      puts("Saindo...");
      break;
    }

    if (op == 1) {
      usuarios_criar_fluxo_escolha();   // escolhe tipo -> cria email/senha -> salva em CSV
      PAUSE();                          // volta ao menu
      continue;
    }

    if (op == 2) {
      Sessao s = login();               // apenas email/senha
      if (!s.autenticado) continue;

      if (!strcmp(s.tipo,"aluno"))      menu_aluno(&s);
      else if (!strcmp(s.tipo,"prof"))  menu_prof(&s);
      else if (!strcmp(s.tipo,"coord")) menu_coord(&s);
      else if (!strcmp(s.tipo,"adm"))   menu_adm(&s);
      else { puts("Tipo desconhecido."); PAUSE(); }
      continue;
    }

    puts("Opcao invalida.");
    PAUSE();
  }

  return 0;
}
