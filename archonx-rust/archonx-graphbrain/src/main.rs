/// archonx-graphbrain binary — replaces Python CLI `python -m archonx.cli graphbrain run`.
///
/// Usage:
///   archonx-graphbrain --mode light    (fast 15-minute cron)
///   archonx-graphbrain --mode full     (deep 8-hour cron)
///
/// Replaces: python -m archonx.cli graphbrain run --mode light|full
use std::path::PathBuf;

use clap::Parser;
use tracing_subscriber::EnvFilter;

use archonx_graphbrain::runtime::{GraphBrainRuntime, RunMode};

#[derive(Parser, Debug)]
#[command(name = "archonx-graphbrain", about = "GraphBrain knowledge graph runner")]
struct Args {
    /// Run mode: light (fast, 15m cron) or full (deep, 8h cron).
    #[arg(long, default_value = "light")]
    mode: RunMode,

    /// Root directory of the archonx-os repository.
    /// Defaults to the current working directory.
    #[arg(long)]
    root: Option<PathBuf>,
}

#[tokio::main]
async fn main() {
    // Initialize tracing — respects RUST_LOG env var
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info")),
        )
        .init();

    let args = Args::parse();
    let root = args.root.unwrap_or_else(|| {
        std::env::current_dir().expect("Cannot determine working directory")
    });

    tracing::info!(
        "archonx-graphbrain starting: mode={}, root={}",
        args.mode,
        root.display()
    );

    let runtime = GraphBrainRuntime::new(root.clone(), args.mode);
    let report = runtime.run().await;

    let report_path = root
        .join("data")
        .join("reports")
        .join("graphbrain_latest.json");

    tracing::info!(
        "Run complete: {} repos, {} docs, {} work orders. Report at {}",
        report.repos_indexed,
        report.docs_indexed,
        report.work_orders.len(),
        report_path.display()
    );

    // Exit with non-zero if no phases completed (indicates total failure)
    if report.phases_completed.is_empty() {
        std::process::exit(1);
    }
}
