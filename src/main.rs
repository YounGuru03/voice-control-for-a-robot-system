//! Native Windows Voice Control Application v2.0
//! 
//! A high-performance native Windows application for voice command recognition
//! with modern Fluent Design UI, real-time transcription, and memory monitoring.
//! 
//! This application completely replaces the Python-based system for improved
//! performance, reliability, and native Windows experience.

#![windows_subsystem = "windows"]

use eframe::egui;
use std::sync::{Arc, Mutex};
use anyhow::Result;
use tracing::{info, error};

mod audio;
mod speech;
mod ui;
mod config;
mod file_output;
mod memory_monitor;
mod utils;

use crate::ui::VoiceControlApp;
use crate::config::Config;

/// Application state shared between components
#[derive(Default)]
pub struct AppState {
    pub is_listening: bool,
    pub last_transcript: String,
    pub last_command: String,
    pub memory_usage_mb: f32,
    pub transcription_history: Vec<(chrono::DateTime<chrono::Local>, String)>,
    pub activity_log: Vec<(chrono::DateTime<chrono::Local>, String, LogLevel)>,
    pub config: Config,
}

#[derive(Debug, Clone)]
pub enum LogLevel {
    Info,
    Warning,
    Error,
    Success,
    Command,
}

impl AppState {
    pub fn add_log_entry(&mut self, message: String, level: LogLevel) {
        self.activity_log.push((chrono::Local::now(), message, level));
        
        // Keep only last 100 log entries to manage memory
        if self.activity_log.len() > 100 {
            self.activity_log.remove(0);
        }
    }
    
    pub fn add_transcription(&mut self, text: String) {
        self.transcription_history.push((chrono::Local::now(), text));
        
        // Keep only last 50 transcriptions
        if self.transcription_history.len() > 50 {
            self.transcription_history.remove(0);
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing for logging
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .init();

    info!("Starting Voice Control Native Application v2.0");

    // Load configuration
    let config = Config::load_or_default()?;
    info!("Configuration loaded successfully");

    // Create shared application state
    let app_state = Arc::new(Mutex::new(AppState {
        config,
        ..Default::default()
    }));

    // Add initial log entry
    {
        let mut state = app_state.lock().unwrap();
        state.add_log_entry(
            "Voice Control Native v2.0 initialized".to_string(), 
            LogLevel::Success
        );
        state.add_log_entry(
            "All native components loaded successfully".to_string(), 
            LogLevel::Info
        );
    }

    // Start memory monitoring in background
    let memory_state = app_state.clone();
    tokio::spawn(async move {
        memory_monitor::start_memory_monitoring(memory_state).await;
    });

    // Start file monitoring in background
    let file_state = app_state.clone();
    tokio::spawn(async move {
        if let Err(e) = file_output::start_file_monitoring(file_state).await {
            error!("File monitoring failed: {}", e);
        }
    });

    info!("Background services started");

    // Configure eframe options for modern Windows appearance
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1200.0, 800.0])
            .with_min_inner_size([1000.0, 600.0])
            .with_icon(load_icon())
            .with_title("Voice Control Native v2.0")
            .with_drag_and_drop(false),
        centered: true,
        ..Default::default()
    };

    info!("Launching application window");

    // Run the application
    eframe::run_native(
        "Voice Control Native v2.0",
        options,
        Box::new(|cc| {
            // Configure egui style for Fluent Design
            configure_fluent_style(&cc.egui_ctx);
            
            Ok(Box::new(VoiceControlApp::new(app_state, cc)))
        }),
    )
    .map_err(|e| anyhow::anyhow!("Failed to run application: {}", e))?;

    info!("Application terminated");
    Ok(())
}

/// Load application icon
fn load_icon() -> egui::IconData {
    // For now, return a default icon. In a full implementation,
    // we'd load a proper .ico file
    egui::IconData {
        rgba: vec![255; 32 * 32 * 4], // Simple white 32x32 icon
        width: 32,
        height: 32,
    }
}

/// Configure egui style for Fluent Design aesthetics
fn configure_fluent_style(ctx: &egui::Context) {
    use egui::{Color32, Rounding, Stroke, Style, Visuals};

    let mut style = Style::default();
    
    // Fluent Design color scheme
    let fluent_blue = Color32::from_rgb(0x00, 0x78, 0xD4);
    let fluent_light_blue = Color32::from_rgb(0xBB, 0xDE, 0xFB);
    let fluent_dark_blue = Color32::from_rgb(0x19, 0x76, 0xD2);
    let fluent_background = Color32::from_rgb(0xF3, 0xF3, 0xF3);
    let fluent_surface = Color32::from_rgb(0xFF, 0xFF, 0xFF);
    let fluent_text = Color32::from_rgb(0x32, 0x32, 0x32);
    let fluent_text_secondary = Color32::from_rgb(0x60, 0x60, 0x60);

    style.visuals = Visuals {
        dark_mode: false,
        override_text_color: Some(fluent_text),
        hyperlink_color: fluent_blue,
        faint_bg_color: fluent_light_blue,
        extreme_bg_color: fluent_background,
        code_bg_color: Color32::from_rgb(0xF5, 0xF5, 0xF5),
        warn_fg_color: Color32::from_rgb(0xFF, 0x98, 0x00),
        error_fg_color: Color32::from_rgb(0xD1, 0x3F, 0x38),
        window_fill: fluent_surface,
        panel_fill: fluent_surface,
        window_stroke: Stroke::new(1.0, fluent_light_blue),
        widgets: style.visuals.widgets.clone(),
        selection: egui::style::Selection {
            bg_fill: fluent_light_blue,
            stroke: Stroke::new(1.0, fluent_blue),
        },
        window_shadow: egui::Shadow {
            offset: [4.0, 4.0].into(),
            blur: 8.0,
            spread: 0.0,
            color: Color32::from_black_alpha(20),
        },
        window_rounding: Rounding::same(8.0),
        menu_rounding: Rounding::same(6.0),
        ..style.visuals
    };

    // Configure widget styles for Fluent Design
    style.visuals.widgets.noninteractive.bg_fill = fluent_surface;
    style.visuals.widgets.noninteractive.fg_stroke = Stroke::new(1.0, fluent_text);
    
    style.visuals.widgets.inactive.bg_fill = fluent_surface;
    style.visuals.widgets.inactive.fg_stroke = Stroke::new(1.0, fluent_text_secondary);
    
    style.visuals.widgets.hovered.bg_fill = fluent_light_blue;
    style.visuals.widgets.hovered.fg_stroke = Stroke::new(1.0, fluent_text);
    
    style.visuals.widgets.active.bg_fill = fluent_blue;
    style.visuals.widgets.active.fg_stroke = Stroke::new(1.0, Color32::WHITE);

    style.visuals.widgets.open.bg_fill = fluent_dark_blue;
    style.visuals.widgets.open.fg_stroke = Stroke::new(1.0, Color32::WHITE);

    // Apply consistent rounding for Fluent Design
    style.visuals.widgets.noninteractive.rounding = Rounding::same(4.0);
    style.visuals.widgets.inactive.rounding = Rounding::same(4.0);
    style.visuals.widgets.hovered.rounding = Rounding::same(4.0);
    style.visuals.widgets.active.rounding = Rounding::same(4.0);
    style.visuals.widgets.open.rounding = Rounding::same(4.0);

    ctx.set_style(style);
}
