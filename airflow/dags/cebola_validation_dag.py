from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'cebola',
    'depends_on_past': False,
    'email': ['alerta@cebola.ai', 'admin@cebola.ai'],
    'email_on_failure': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=15)
}

with DAG(
    'cebola_validation_dag',
    default_args=default_args,
    description='Validação diária do ecossistema Cebola Vx0 - CPU Only',
    schedule_interval='0 5 * * *',  # 05:00 UTC diariamente
    start_date=datetime(2024, 5, 1),
    catchup=False,
    tags=['cebola', 'validacao', 'producao'],
    params={
        'input_dir': '/cebola_vx0/tecnicos/',
        'output_dir': '/cebola_vx0/validacao/',
        'log_dir': '/cebola_vx0/logs/'
    }
) as dag:
    
    sanitizar = BashOperator(
        task_id='sanitizacao_avancada',
        bash_command='''
        cebola sanitize \
        --input {{ params.input_dir }} \
        --output {{ params.output_dir }} \
        --patterns "!sudo|rm -rf|override|--no-preserve-root" \
        --hash sha256 \
        --concurrency 4
        ''',
        retries=2,
        retry_delay=timedelta(minutes=10)
    )
    
    validar = BashOperator(
        task_id='validacao_cross_model',
        bash_command='''
        cebola validate \
        --models phi3:3.8b-mini-128k-instruct-q4_0,tinyllama \
         --threshold 0.85' \
        --log {{ params.log_dir }}validacao_$(date +%Y%m%d).log \
        --timeout 300
        ''',
        retries=3,
        retry_delay=timedelta(minutes=20)
    )
    
    relatorio = BashOperator(
        task_id='geracao_relatorio_consolidado',
        bash_command='''
        cebola report \
        --daily \
        --input {{ params.log_dir }} \
        --output /cebola_vx0/resumo/resumo-diario_$(date +%Y%m%d).md \
        --format markdown \
        --compress
        ''',
        retries=1
    )

    # Fluxo de execução otimizado
    sanitizar >> validar >> relatorio

    # Validação pós-tarefas
    validar >> BashOperator(
        task_id='verificacao_final',
        bash_command='''
        cebola check \
        --file /cebola_vx0/resumo/resumo-diario_$(date +%Y%m%d).md \
        --hash $(sha256sum /cebola_vx0/resumo/resumo-diario_$(date +%Y%m%d).md | cut -d" " -f1)
        '''
    )
