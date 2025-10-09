// 奈克赛斯奥特曼开场动画JavaScript
class UltramanIntro {
    constructor() {
        this.introElement = null;
        this.isVisible = true;
        this.duration = 5000; // 5秒动画
    }

    // 创建开场动画HTML
    createIntroHTML () {
        return `
        <div class="ultraman-intro" id="ultraman-intro">
            <div class="stars"></div>
            <div class="particles" id="particles"></div>
            
            <div class="energy-ring"></div>
            <div class="energy-burst" style="top: 50%; left: 50%; transform: translate(-50%, -50%);"></div>
            <div class="energy-burst" style="top: 50%; left: 50%; transform: translate(-50%, -50%); animation-delay: 0.5s;"></div>
            <div class="energy-burst" style="top: 50%; left: 50%; transform: translate(-50%, -50%); animation-delay: 1s;"></div>
            
            <div class="ultraman-logo">
                <img src="/Users/gyw/Desktop/Project/2025/zyj_text_mining/library/web_sources/奥特曼1.png" 
                     alt="Ultraman" class="ultraman-icon" />
            </div>
            
            <h1 class="ultraman-title">NEXUS ULTRA</h1>
            <p class="ultraman-subtitle">Literature Analysis System</p>
            <p class="ultraman-text">Based on R-Bibliometrix & VOSviewer</p>
            
            <div class="loading-bar">
                <div class="loading-progress"></div>
            </div>
            
            <p class="ultraman-text">Initializing System...</p>
        </div>
        `;
    }

    // 创建粒子效果
    createParticles () {
        const particlesContainer = document.getElementById('particles');
        if (!particlesContainer) return;

        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 6 + 's';
            particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
            particlesContainer.appendChild(particle);
        }
    }

    // 显示开场动画
    show () {
        // 创建动画HTML
        const introHTML = this.createIntroHTML();
        document.body.insertAdjacentHTML('afterbegin', introHTML);

        this.introElement = document.getElementById('ultraman-intro');

        // 创建粒子效果
        setTimeout(() => {
            this.createParticles();
        }, 500);

        // 设置自动隐藏
        setTimeout(() => {
            this.hide();
        }, this.duration);
    }

    // 隐藏开场动画
    hide () {
        if (this.introElement) {
            this.introElement.classList.add('hide-intro');

            setTimeout(() => {
                if (this.introElement && this.introElement.parentNode) {
                    this.introElement.parentNode.removeChild(this.introElement);
                }
                this.isVisible = false;
            }, 1000);
        }
    }

    // 手动隐藏
    hideManual () {
        this.hide();
    }

    // 检查是否可见
    isIntroVisible () {
        return this.isVisible;
    }
}

// 全局函数
window.showUltramanIntro = function () {
    const intro = new UltramanIntro();
    intro.show();
    return intro;
};

// 页面加载完成后自动显示动画
document.addEventListener('DOMContentLoaded', function () {
    // 检查是否已经显示过动画
    const hasShownIntro = sessionStorage.getItem('ultraman-intro-shown');

    if (!hasShownIntro) {
        const intro = new UltramanIntro();
        intro.show();

        // 标记已显示
        sessionStorage.setItem('ultraman-intro-shown', 'true');
    }
});

// 导出类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UltramanIntro;
}






