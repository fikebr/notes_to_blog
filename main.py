"""
Main entry point for Notes to Blog Application.
Provides a CLI for processing notes, batch jobs, config management, and status reporting.
"""
import sys
import time
import traceback
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

from src.logger import setup_logging
from src.models.config_models import Config
from src.services.input_processor import InputProcessor
from src.services.output_generator import OutputGenerator
from src.crews.blog_post_crew import BlogPostCrew

app = typer.Typer(help="Notes to Blog: Convert notes to blog posts using AI agents.")
console = Console()

# Global config and logger
config: Optional[Config] = None
logger = None


def load_config() -> Config:
    """Load and validate application config."""
    from src.models.config_models import Config
    try:
        cfg = Config.model_validate({})  # Loads from .env if set up
        return cfg
    except Exception as e:
        console.print(f"[red]Config error:[/red] {e}")
        raise


def init():
    """Initialize config and logging."""
    global config, logger
    config = load_config()
    logger = setup_logging()
    logger.info("Application started")


@app.command()
def process_file(
    file: Path = typer.Argument(..., exists=True, readable=True, help="Path to note file to process."),
    output: Optional[Path] = typer.Option(None, help="Output directory for blog post."),
):
    """Process a single note file into a blog post."""
    init()
    try:
        input_processor = InputProcessor()
        note = input_processor.parse_note(file.read_text(), file.name, file.suffix.lstrip('.'))
        crew = BlogPostCrew(config)
        blog_post = crew.process_note(note)
        output_gen = OutputGenerator()
        out_dir = output or config.paths.output_dir
        out_path = output_gen.generate_markdown_file(blog_post, output_dir=out_dir)
        console.print(f"[green]Blog post generated:[/green] {out_path}")
        logger.info(f"Processed file: {file} -> {out_path}")
    except Exception as e:
        logger.error(f"Error processing file {file}: {e}")
        console.print(f"[red]Error:[/red] {e}")
        if config and config.app.debug:
            traceback.print_exc()
        raise typer.Exit(code=1)


@app.command()
def process_batch(
    inbox: Optional[Path] = typer.Option(None, help="Inbox directory to scan for notes."),
    output: Optional[Path] = typer.Option(None, help="Output directory for blog posts."),
):
    """Process all note files in the inbox directory."""
    init()
    input_processor = InputProcessor()
    inbox_dir = inbox or config.paths.inbox_dir
    output_dir = output or config.paths.output_dir
    files = list(inbox_dir.glob("*.md")) + list(inbox_dir.glob("*.txt"))
    if not files:
        console.print(f"[yellow]No note files found in {inbox_dir}.[/yellow]")
        raise typer.Exit()
    crew = BlogPostCrew(config)
    output_gen = OutputGenerator()
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), TimeElapsedColumn(), console=console) as progress:
        task = progress.add_task("Processing notes...", total=len(files))
        for file in files:
            try:
                note = input_processor.parse_note(file.read_text(), file.name, file.suffix.lstrip('.'))
                blog_post = crew.process_note(note)
                out_path = output_gen.generate_markdown_file(blog_post, output_dir=output_dir)
                logger.info(f"Processed file: {file} -> {out_path}")
                progress.console.print(f"[green]Processed:[/green] {file.name} -> {out_path.name}")
            except Exception as e:
                logger.error(f"Error processing file {file}: {e}")
                progress.console.print(f"[red]Error processing {file.name}:[/red] {e}")
                if config and config.app.debug:
                    traceback.print_exc()
            progress.update(task, advance=1)
    console.print(f"[bold green]Batch processing complete. {len(files)} files processed.[/bold green]")


@app.command()
def config_cmd(
    show: bool = typer.Option(False, "--show", help="Show current configuration."),
    validate: bool = typer.Option(False, "--validate", help="Validate configuration."),
    reload: bool = typer.Option(False, "--reload", help="Reload configuration from file."),
):
    """Show, validate, or reload configuration."""
    global config
    if show:
        cfg = config or load_config()
        table = Table(title="Current Configuration")
        for section, value in cfg.model_dump().items():
            table.add_row(str(section), str(value))
        console.print(table)
    if validate:
        try:
            cfg = config or load_config()
            cfg.model_validate(cfg.model_dump())
            console.print("[green]Configuration is valid.[/green]")
        except Exception as e:
            console.print(f"[red]Configuration invalid:[/red] {e}")
            raise typer.Exit(code=1)
    if reload:
        config = load_config()
        console.print("[green]Configuration reloaded.[/green]")


@app.command()
def status():
    """Show last run status and recent logs."""
    log_path = config.paths.log_file if config else Path("./logs/app.log")
    console.print(Panel(f"[bold]Notes to Blog Application Status[/bold]\nLog file: {log_path}"))
    if log_path.exists():
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-20:]
            for line in lines:
                console.print(line.rstrip())
    else:
        console.print("[yellow]No log file found.[/yellow]")


def main():
    try:
        app()
    except KeyboardInterrupt:
        if logger:
            logger.info("Application interrupted by user.")
        console.print("[yellow]Interrupted by user.[/yellow]")
        raise typer.Exit(code=130)
    except Exception as e:
        if logger:
            logger.error(f"Fatal error: {e}")
        console.print(f"[red]Fatal error:[/red] {e}")
        if config and config.app.debug:
            traceback.print_exc()
        raise typer.Exit(code=1)


if __name__ == "__main__":
    main()
