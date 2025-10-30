# ============================================================================
# deployment_builder.py
# ============================================================================

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

class DeploymentBuilder:
    """优化的部署构建器"""
    
    def __init__(self, project_dir: str = "."):
        """初始化部署构建器"""
        self.project_dir = os.path.abspath(project_dir)
        self.deployment_dir = os.path.join(self.project_dir, "deployment")
        self.dist_dir = os.path.join(self.project_dir, "dist")
        self.build_dir = os.path.join(self.project_dir, "build")
        
        print(f"🔧 DeploymentBuilder initialized")
        print(f"   Project: {self.project_dir}")
        print(f"   Deployment: {self.deployment_dir}")
    
    def check_dependencies(self) -> Dict[str, bool]:
        """检查依赖"""
        dependencies = {
            "pyinstaller": False,
            "faster-whisper": False,
            "pyttsx3": False,
            "numpy": False,
            "pyaudio": False,
            "tkinter": False
        }
        
        for dep in dependencies.keys():
            try:
                if dep == "tkinter":
                    import tkinter
                    dependencies[dep] = True
                elif dep == "pyinstaller":
                    import PyInstaller
                    dependencies[dep] = True
                elif dep == "faster-whisper":
                    import faster_whisper
                    dependencies[dep] = True
                elif dep == "pyttsx3":
                    import pyttsx3
                    dependencies[dep] = True
                elif dep == "numpy":
                    import numpy
                    dependencies[dep] = True
                elif dep == "pyaudio":
                    import pyaudio
                    dependencies[dep] = True
            except ImportError:
                dependencies[dep] = False
        
        print("📋 Dependency Check:")
        for dep, available in dependencies.items():
            status = "✅" if available else "❌"
            print(f"   {status} {dep}")
        
        return dependencies
    
    def generate_spec_file(self, main_script: str = "main_voice_app.py") -> str:
        """生成PyInstaller spec文件"""
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 获取spec文件目录
spec_root = os.path.dirname(os.path.abspath(SPEC))

# 数据文件
datas = []

# 添加本地模型目录
models_dir = os.path.join(spec_root, "local_models")
if os.path.exists(models_dir):
    for model_name in os.listdir(models_dir):
        model_path = os.path.join(models_dir, model_name)
        if os.path.isdir(model_path):
            datas.append((model_path, f"local_models/{{model_name}}"))

# 添加配置文件
config_files = [
    "commands_hotwords.json",
    "speakers.json", 
    "tts_config.json"
]

for config_file in config_files:
    config_path = os.path.join(spec_root, config_file)
    if os.path.exists(config_path):
        datas.append((config_path, "."))

# 隐藏导入
hiddenimports = [
    'faster_whisper',
    'whisper',
    'pyttsx3',
    'numpy',
    'pyaudio',
    'wave',
    'json',
    'threading',
    'queue',
    'datetime',
    'pathlib',
    'uuid',
    're'
]

# 分析
a = Analysis(
    ['{main_script}'],
    pathex=[spec_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy', 
        'pandas',
        'IPython',
        'jupyter'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VoiceControlSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为False隐藏控制台
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
        
        spec_file = os.path.join(self.project_dir, "voice_control_system.spec")
        
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"✅ Generated spec file: {spec_file}")
        return spec_file
    
    def build_executable(self, spec_file: str = None, clean: bool = True) -> bool:
        """构建可执行文件"""
        
        if clean:
            self.clean_build_files()
        
        if not spec_file:
            spec_file = self.generate_spec_file()
        
        try:
            print("🔨 Building executable with PyInstaller...")
            print(f"   Using spec file: {spec_file}")
            
            # 运行PyInstaller
            cmd = [sys.executable, "-m", "PyInstaller", "--clean", spec_file]
            
            result = subprocess.run(cmd, cwd=self.project_dir, 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Executable built successfully")
                
                # 检查可执行文件
                exe_name = "VoiceControlSystem.exe" if os.name == "nt" else "VoiceControlSystem"
                exe_path = os.path.join(self.dist_dir, exe_name)
                
                if os.path.exists(exe_path):
                    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                    print(f"📦 Executable created: {exe_path}")
                    print(f"   Size: {size_mb:.1f} MB")
                    return True
                else:
                    print("❌ Executable file not found after build")
                    return False
            else:
                print(f"❌ PyInstaller build failed:")
                print(f"   STDOUT: {result.stdout}")
                print(f"   STDERR: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Build error: {e}")
            return False
    
    def clean_build_files(self):
        """清理构建文件"""
        dirs_to_clean = [self.dist_dir, self.build_dir]
        
        for dir_path in dirs_to_clean:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    print(f"🧹 Cleaned: {dir_path}")
                except Exception as e:
                    print(f"⚠️ Could not clean {dir_path}: {e}")
    
    def create_deployment_package(self) -> bool:
        """创建部署包"""
        try:
            # 创建部署目录
            os.makedirs(self.deployment_dir, exist_ok=True)
            
            # 复制可执行文件
            exe_name = "VoiceControlSystem.exe" if os.name == "nt" else "VoiceControlSystem"
            exe_source = os.path.join(self.dist_dir, exe_name)
            exe_dest = os.path.join(self.deployment_dir, exe_name)
            
            if os.path.exists(exe_source):
                shutil.copy2(exe_source, exe_dest)
                print(f"📦 Copied executable to deployment package")
            else:
                print("❌ Executable not found for packaging")
                return False
            
            # 创建README文件
            readme_content = f'''# Voice Control System - Deployment Package


构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
版本: Voice Control System v3.0
'''
            
            readme_path = os.path.join(self.deployment_dir, "README.txt")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # 创建部署信息
            deployment_info = {
                "name": "Voice Control System",
                "version": "3.0",
                "build_date": datetime.now().isoformat(),
                "executable": exe_name,
                "features": [
                    "完全离线运行",
                    "智能命令管理", 
                    "语音指令播报",
                    "嵌入式模型",
                    "独立可执行文件"
                ]
            }
            
            info_path = os.path.join(self.deployment_dir, "deployment_info.json")
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(deployment_info, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Deployment package created: {self.deployment_dir}")
            
            # 计算包大小
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.deployment_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            
            size_mb = total_size / (1024 * 1024)
            print(f"📦 Package size: {size_mb:.1f} MB")
            
            return True
            
        except Exception as e:
            print(f"❌ Deployment package creation error: {e}")
            return False
    
    def full_deployment_workflow(self) -> bool:
        """完整部署流程"""
        print("🚀 Starting full deployment workflow...")
        
        # 检查依赖
        dependencies = self.check_dependencies()
        missing = [dep for dep, available in dependencies.items() if not available and dep != "tkinter"]
        if missing:
            print(f"⚠️ Missing dependencies: {', '.join(missing)}")
            print("Please install them with: pip install " + " ".join(missing))
        
        # 生成spec文件
        spec_file = self.generate_spec_file()
        
        # 构建可执行文件
        if not self.build_executable(spec_file):
            print("❌ Executable build failed")
            return False
        
        # 创建部署包
        if not self.create_deployment_package():
            print("❌ Deployment package creation failed")
            return False
        
        print("✅ Full deployment workflow completed successfully!")
        print(f"📦 Deployment package ready: {self.deployment_dir}")
        
        return True

def main():
    """主部署脚本"""
    print("=" * 60)
    print("Voice Control System - Deployment Builder")
    print("=" * 60)
    
    # 初始化构建器
    builder = DeploymentBuilder()
    
    # 运行完整流程
    success = builder.full_deployment_workflow()
    
    if success:
        print("\\n🎉 Deployment completed successfully!")
        print("\\nNext steps:")
        print("1. Test the executable in the deployment folder")
        print("2. Distribute the deployment package")
        print("3. Provide the README.txt to end users")
    else:
        print("\\n❌ Deployment failed. Check the error messages above.")
    
    print("\\n" + "=" * 60)

if __name__ == "__main__":
    main()