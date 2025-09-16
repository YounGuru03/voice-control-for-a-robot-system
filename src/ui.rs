//! Modern Fluent Design UI for the Voice Control application
//! 
//! Implements a three-panel layout with real-time transcription display,
//! memory usage monitoring, and responsive animations.

use eframe::egui::{self, *};
use std::sync::{Arc, Mutex};
use crate::{AppState, LogLevel};
use crate::speech::SpeechProcessor;
use tracing::{info, error};

pub struct VoiceControlApp {
    app_state: Arc<Mutex<AppState>>,
    speech_processor: Option<SpeechProcessor>,
    
    // UI state
    show_settings: bool,
    settings_window_open: bool,
    last_memory_update: std::time::Instant,
    animation_time: f32,
    
    // UI styling
    header_color: Color32,
    panel_color: Color32,
    accent_color: Color32,
    success_color: Color32,
    warning_color: Color32,
    error_color: Color32,
}

impl VoiceControlApp {
    pub fn new(app_state: Arc<Mutex<AppState>>, _cc: &eframe::CreationContext<'_>) -> Self {
        // Use default system fonts for now
        // In production, we'd load custom fonts here
        
        // Initialize speech processor
        let speech_processor = match SpeechProcessor::new() {
            Ok(processor) => {
                info!("Speech processor initialized successfully");
                Some(processor)
            }
            Err(e) => {
                error!("Failed to initialize speech processor: {}", e);
                let mut state = app_state.lock().unwrap();
                state.add_log_entry(
                    format!("Failed to initialize speech processor: {}", e),
                    LogLevel::Error,
                );
                None
            }
        };
        
        Self {
            app_state,
            speech_processor,
            show_settings: false,
            settings_window_open: false,
            last_memory_update: std::time::Instant::now(),
            animation_time: 0.0,
            
            // Fluent Design colors
            header_color: Color32::from_rgb(0x00, 0x78, 0xD4),
            panel_color: Color32::from_rgb(0xFF, 0xFF, 0xFF),
            accent_color: Color32::from_rgb(0x00, 0x78, 0xD4),
            success_color: Color32::from_rgb(0x10, 0x89, 0x3E),
            warning_color: Color32::from_rgb(0xFF, 0x98, 0x00),
            error_color: Color32::from_rgb(0xD1, 0x3F, 0x38),
        }
    }
    
    fn draw_header(&mut self, ui: &mut Ui) {
        ui.horizontal(|ui| {
            ui.spacing_mut().item_spacing.x = 16.0;
            
            // App title with gradient effect
            ui.add_space(8.0);
            let _title_response = ui.colored_label(
                self.header_color,
                RichText::new("🎤 Voice Control Native v2.0")
                    .size(24.0)
                    .strong()
            );
            
            ui.add_space(16.0);
            ui.colored_label(
                Color32::from_rgb(0x60, 0x60, 0x60),
                RichText::new("High-Performance Native Windows Application")
                    .size(12.0)
            );
            
            ui.with_layout(Layout::right_to_left(Align::Center), |ui| {
                // Settings button with Fluent Design styling
                let settings_button = ui.add_sized(
                    [100.0, 36.0],
                    Button::new("⚙ Settings")
                        .fill(self.accent_color)
                        .rounding(Rounding::same(6.0))
                );
                
                if settings_button.clicked() {
                    self.show_settings = true;
                    self.settings_window_open = true;
                }
                
                ui.add_space(16.0);
                
                // Memory usage display
                let memory_mb = {
                    let state = self.app_state.lock().unwrap();
                    state.memory_usage_mb
                };
                
                ui.colored_label(
                    if memory_mb > 100.0 { self.warning_color } else { Color32::GRAY },
                    format!("Memory: {:.1} MB", memory_mb)
                );
            });
        });
        
        ui.add_space(8.0);
        ui.separator();
        ui.add_space(8.0);
    }
    
    fn draw_control_panel(&mut self, ui: &mut Ui) {
        Frame::none()
            .fill(self.panel_color)
            .rounding(Rounding::same(8.0))
            .inner_margin(Margin::same(16.0))
            .shadow(egui::Shadow {
                offset: [2.0, 2.0].into(),
                blur: 4.0,
                spread: 0.0,
                color: Color32::from_black_alpha(30),
            })
            .show(ui, |ui| {
                ui.vertical_centered(|ui| {
                    ui.colored_label(
                        self.header_color,
                        RichText::new("Voice Control")
                            .size(18.0)
                            .strong()
                    );
                    
                    ui.add_space(12.0);
                    
                    let is_listening = {
                        let state = self.app_state.lock().unwrap();
                        state.is_listening
                    };
                    
                    // Main control button with animation
                    let button_color = if is_listening {
                        self.error_color
                    } else {
                        self.accent_color
                    };
                    
                    let button_text = if is_listening {
                        "🛑 Stop Listening"
                    } else {
                        "🎙 Start Listening"
                    };
                    
                    // Add pulsing animation when listening
                    let button_alpha = if is_listening {
                        let pulse = (self.animation_time * 3.0).sin() * 0.2 + 0.8;
                        (255.0 * pulse) as u8
                    } else {
                        255
                    };
                    
                    let animated_color = Color32::from_rgba_premultiplied(
                        button_color.r(),
                        button_color.g(),
                        button_color.b(),
                        button_alpha,
                    );
                    
                    let control_button = ui.add_sized(
                        [200.0, 48.0],
                        Button::new(RichText::new(button_text).size(16.0))
                            .fill(animated_color)
                            .rounding(Rounding::same(8.0))
                    );
                    
                    if control_button.clicked() {
                        self.toggle_listening();
                    }
                    
                    ui.add_space(16.0);
                    
                    // Status indicator
                    let status_text = if is_listening {
                        "🔴 Listening..."
                    } else {
                        "⚪ Ready"
                    };
                    
                    let status_color = if is_listening {
                        self.error_color
                    } else {
                        self.success_color
                    };
                    
                    ui.colored_label(status_color, RichText::new(status_text).size(14.0));
                    
                    ui.add_space(16.0);
                    ui.separator();
                    ui.add_space(16.0);
                    
                    // Last command display
                    ui.colored_label(
                        self.header_color,
                        RichText::new("Last Command").size(16.0).strong()
                    );
                    
                    ui.add_space(8.0);
                    
                    let last_command = {
                        let state = self.app_state.lock().unwrap();
                        state.last_command.clone()
                    };
                    
                    Frame::none()
                        .fill(Color32::from_rgb(0xBB, 0xDE, 0xFB))
                        .rounding(Rounding::same(6.0))
                        .inner_margin(Margin::same(12.0))
                        .show(ui, |ui| {
                            ui.colored_label(
                                Color32::from_rgb(0x32, 0x32, 0x32),
                                if last_command.is_empty() {
                                    "None"
                                } else {
                                    &last_command
                                }
                            );
                        });
                });
            });
    }
    
    fn draw_transcription_panel(&mut self, ui: &mut Ui) {
        Frame::none()
            .fill(self.panel_color)
            .rounding(Rounding::same(8.0))
            .inner_margin(Margin::same(16.0))
            .shadow(egui::Shadow {
                offset: [2.0, 2.0].into(),
                blur: 4.0,
                spread: 0.0,
                color: Color32::from_black_alpha(30),
            })
            .show(ui, |ui| {
                ui.vertical(|ui| {
                    // Header with clear button
                    ui.horizontal(|ui| {
                        ui.colored_label(
                            self.header_color,
                            RichText::new("Live Transcription").size(18.0).strong()
                        );
                        
                        ui.with_layout(Layout::right_to_left(Align::Center), |ui| {
                            let clear_button = ui.add_sized(
                                [80.0, 28.0],
                                Button::new("Clear")
                                    .fill(Color32::from_rgb(0xE1, 0xE1, 0xE1))
                                    .rounding(Rounding::same(4.0))
                            );
                            
                            if clear_button.clicked() {
                                let mut state = self.app_state.lock().unwrap();
                                state.transcription_history.clear();
                                state.add_log_entry(
                                    "Transcription history cleared".to_string(),
                                    LogLevel::Info,
                                );
                            }
                        });
                    });
                    
                    ui.add_space(12.0);
                    
                    // Transcription display area
                    ScrollArea::vertical()
                        .max_height(300.0)
                        .show(ui, |ui| {
                            let transcription_history = {
                                let state = self.app_state.lock().unwrap();
                                state.transcription_history.clone()
                            };
                            
                            if transcription_history.is_empty() {
                                ui.centered_and_justified(|ui| {
                                    ui.colored_label(
                                        Color32::from_rgb(0x80, 0x80, 0x80),
                                        "No transcriptions yet.\nStart listening to see real-time speech-to-text."
                                    );
                                });
                            } else {
                                for (timestamp, text) in transcription_history.iter().rev() {
                                    ui.horizontal(|ui| {
                                        ui.colored_label(
                                            Color32::from_rgb(0x60, 0x60, 0x60),
                                            format!("[{}]", timestamp.format("%H:%M:%S"))
                                        );
                                        
                                        ui.colored_label(
                                            Color32::from_rgb(0x32, 0x32, 0x32),
                                            text
                                        );
                                    });
                                    
                                    ui.add_space(4.0);
                                }
                            }
                        });
                });
            });
    }
    
    fn draw_activity_log(&mut self, ui: &mut Ui) {
        Frame::none()
            .fill(self.panel_color)
            .rounding(Rounding::same(8.0))
            .inner_margin(Margin::same(16.0))
            .shadow(egui::Shadow {
                offset: [2.0, 2.0].into(),
                blur: 4.0,
                spread: 0.0,
                color: Color32::from_black_alpha(30),
            })
            .show(ui, |ui| {
                ui.vertical(|ui| {
                    // Header with clear button
                    ui.horizontal(|ui| {
                        ui.colored_label(
                            self.header_color,
                            RichText::new("Activity Log").size(18.0).strong()
                        );
                        
                        ui.with_layout(Layout::right_to_left(Align::Center), |ui| {
                            let clear_button = ui.add_sized(
                                [80.0, 28.0],
                                Button::new("Clear")
                                    .fill(Color32::from_rgb(0xE1, 0xE1, 0xE1))
                                    .rounding(Rounding::same(4.0))
                            );
                            
                            if clear_button.clicked() {
                                let mut state = self.app_state.lock().unwrap();
                                state.activity_log.clear();
                                state.add_log_entry(
                                    "Activity log cleared".to_string(),
                                    LogLevel::Info,
                                );
                            }
                        });
                    });
                    
                    ui.add_space(12.0);
                    
                    // Log display area
                    ScrollArea::vertical()
                        .max_height(200.0)
                        .stick_to_bottom(true)
                        .show(ui, |ui| {
                            let activity_log = {
                                let state = self.app_state.lock().unwrap();
                                state.activity_log.clone()
                            };
                            
                            for (timestamp, message, level) in activity_log.iter() {
                                let color = match level {
                                    LogLevel::Error => self.error_color,
                                    LogLevel::Warning => self.warning_color,
                                    LogLevel::Success => self.success_color,
                                    LogLevel::Command => self.accent_color,
                                    LogLevel::Info => Color32::from_rgb(0x60, 0x60, 0x60),
                                };
                                
                                ui.horizontal(|ui| {
                                    ui.colored_label(
                                        Color32::from_rgb(0x80, 0x80, 0x80),
                                        format!("[{}]", timestamp.format("%H:%M:%S"))
                                    );
                                    
                                    ui.colored_label(color, message);
                                });
                                
                                ui.add_space(2.0);
                            }
                        });
                });
            });
    }
    
    fn toggle_listening(&mut self) {
        let is_listening = {
            let state = self.app_state.lock().unwrap();
            state.is_listening
        };
        
        if is_listening {
            // Stop listening
            if let Some(ref mut processor) = self.speech_processor {
                if let Err(e) = processor.stop_listening() {
                    error!("Failed to stop listening: {}", e);
                    let mut state = self.app_state.lock().unwrap();
                    state.add_log_entry(
                        format!("Failed to stop listening: {}", e),
                        LogLevel::Error,
                    );
                    return;
                }
            }
            
            let mut state = self.app_state.lock().unwrap();
            state.is_listening = false;
            state.add_log_entry("Stopped listening".to_string(), LogLevel::Info);
        } else {
            // Start listening
            if let Some(ref mut processor) = self.speech_processor {
                match processor.start_listening(self.app_state.clone()) {
                    Ok(()) => {
                        let mut state = self.app_state.lock().unwrap();
                        state.is_listening = true;
                        state.add_log_entry("Started listening for voice commands".to_string(), LogLevel::Success);
                    }
                    Err(e) => {
                        error!("Failed to start listening: {}", e);
                        let mut state = self.app_state.lock().unwrap();
                        state.add_log_entry(
                            format!("Failed to start listening: {}", e),
                            LogLevel::Error,
                        );
                    }
                }
            } else {
                let mut state = self.app_state.lock().unwrap();
                state.add_log_entry(
                    "Speech processor not available".to_string(),
                    LogLevel::Error,
                );
            }
        }
    }
    
    fn show_settings_window(&mut self, ctx: &Context) {
        if !self.settings_window_open {
            return;
        }
        
        egui::Window::new("Settings")
            .resizable(false)
            .collapsible(false)
            .default_width(400.0)
            .show(ctx, |ui| {
                let mut config = {
                    let state = self.app_state.lock().unwrap();
                    state.config.clone()
                };
                
                ui.vertical_centered(|ui| {
                    ui.colored_label(
                        self.header_color,
                        RichText::new("Voice Control Settings").size(18.0).strong()
                    );
                });
                
                ui.add_space(16.0);
                
                // Confidence threshold
                ui.label("Speech Recognition Confidence Threshold:");
                let _confidence_response = ui.add(
                    Slider::new(&mut config.confidence_threshold, 0.0..=1.0)
                        .text("Confidence")
                        .show_value(true)
                );
                
                ui.add_space(8.0);
                
                // Recording duration
                ui.label("Recording Duration (seconds):");
                let _duration_response = ui.add(
                    Slider::new(&mut config.recording_duration, 0.5..=10.0)
                        .text("Duration")
                        .show_value(true)
                );
                
                ui.add_space(8.0);
                
                // Checkboxes for features
                ui.checkbox(&mut config.enable_preprocessing, "Enable Audio Preprocessing");
                ui.checkbox(&mut config.show_transcription, "Show Real-time Transcription");
                ui.checkbox(&mut config.monitor_memory, "Monitor Memory Usage");
                
                ui.add_space(16.0);
                ui.separator();
                ui.add_space(8.0);
                
                // Buttons
                ui.horizontal(|ui| {
                    if ui.button("Cancel").clicked() {
                        self.settings_window_open = false;
                    }
                    
                    ui.with_layout(Layout::right_to_left(Align::Center), |ui| {
                        if ui.button("Save").clicked() {
                            let validated_config = config.validate();
                            
                            {
                                let mut state = self.app_state.lock().unwrap();
                                state.config = validated_config.clone();
                                state.add_log_entry("Settings saved".to_string(), LogLevel::Success);
                            }
                            
                            if let Err(e) = validated_config.save() {
                                error!("Failed to save config: {}", e);
                                let mut state = self.app_state.lock().unwrap();
                                state.add_log_entry(
                                    format!("Failed to save settings: {}", e),
                                    LogLevel::Error,
                                );
                            }
                            
                            self.settings_window_open = false;
                        }
                    });
                });
            });
    }
}

impl eframe::App for VoiceControlApp {
    fn update(&mut self, ctx: &Context, _frame: &mut eframe::Frame) {
        // Update animation time
        self.animation_time += ctx.input(|i| i.stable_dt);
        
        // Request repaint for animations
        ctx.request_repaint();
        
        // Show settings window if requested
        if self.show_settings {
            self.show_settings_window(ctx);
            self.show_settings = false;
        }
        
        // Main application layout
        CentralPanel::default()
            .frame(Frame::none().fill(Color32::from_rgb(0xF3, 0xF3, 0xF3)))
            .show(ctx, |ui| {
                ui.vertical(|ui| {
                    // Header
                    self.draw_header(ui);
                    
                    // Main content - three-column layout
                    ui.horizontal(|ui| {
                        ui.spacing_mut().item_spacing.x = 12.0;
                        
                        // Left panel - Controls (25%)
                        ui.allocate_ui_with_layout(
                            [ui.available_width() * 0.25, ui.available_height()].into(),
                            Layout::top_down(Align::LEFT),
                            |ui| {
                                self.draw_control_panel(ui);
                            },
                        );
                        
                        // Center panel - Transcription (45%)
                        ui.allocate_ui_with_layout(
                            [ui.available_width() * 0.6, ui.available_height()].into(),
                            Layout::top_down(Align::LEFT),
                            |ui| {
                                self.draw_transcription_panel(ui);
                            },
                        );
                        
                        // Right panel - Activity Log (30%)
                        ui.allocate_ui_with_layout(
                            [ui.available_width(), ui.available_height()].into(),
                            Layout::top_down(Align::LEFT),
                            |ui| {
                                self.draw_activity_log(ui);
                            },
                        );
                    });
                });
            });
    }
    
    fn on_exit(&mut self, _gl: Option<&eframe::glow::Context>) {
        info!("Application shutting down");
        
        // Stop listening if active
        if let Some(ref mut processor) = self.speech_processor {
            let _ = processor.stop_listening();
        }
        
        // Save configuration
        let config = {
            let state = self.app_state.lock().unwrap();
            state.config.clone()
        };
        
        if let Err(e) = config.save() {
            error!("Failed to save config on exit: {}", e);
        }
    }
}