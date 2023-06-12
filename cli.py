import click

from api import api_start as api_start
from cli_demo import main as cli_start
from configs.model_config import llm_model_dict, embedding_model_dict


@click.group()
@click.version_option(version='1.0.0')
@click.pass_context
def cli(ctx):
    pass


@cli.group()
def llm():
    pass


@llm.command(name="ls")
def llm_ls():
    for k in llm_model_dict.keys():
        print(k)


@cli.group()
def embedding():
    pass


@embedding.command(name="ls")
def embedding_ls():
    for k in embedding_model_dict.keys():
        print(k)


@cli.group()
def start():
    pass


@start.command(name="api", context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-i', '--ip', default='0.0.0.0', show_default=True, type=str, help='api_server listen address.')
@click.option('-p', '--port', default=7861, show_default=True, type=int, help='api_server listen port.')
def start_api(ip, port):
    # 调用api_start之前需要先loadCheckPoint,并传入加载检查点的参数，
    # 理论上可以用click包进行包装，但过于繁琐，改动较大，
    # 此处仍用parser包，并以models.loader.args.DEFAULT_ARGS的参数为默认参数
    # 如有改动需要可以更改models.loader.args.DEFAULT_ARGS
    from models import shared
    from models.loader import LoaderCheckPoint
    from models.loader.args import DEFAULT_ARGS
    shared.loaderCheckPoint = LoaderCheckPoint(DEFAULT_ARGS)
    api_start(host=ip, port=port)


@start.command(name="cli", context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-i', '--info', default="start client", show_default=True, type=str)
def start_cli(info):
    print(info)

    from models.loader.args import parser
    cli_start()
    


@start.command(name="webui", context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-i', '--info', default="start client", show_default=True, type=str)
def start_webui(info):
    print(info)
    import webui


cli()
