/**
 * Data Cache Manager - نظام إدارة البيانات المخزنة
 * يحسن الأداء بتخزين البيانات في localStorage
 */

class DataCacheManager {
    constructor() {
        this.CACHE_VERSION = '1.0.0';
        this.CACHE_DURATION = 5 * 60 * 1000; // 5 دقائق
        this.API_BASE = window.API_BASE || 'http://localhost:8000/api';
        
        this.cacheKeys = {
            GRADES: 'cache_grades',
            SECTIONS: 'cache_sections_',  // + gradeId
            PROJECTS: 'cache_projects',
            STATS: 'cache_stats',
            TEACHER: 'cache_teacher',
            SUBJECTS: 'cache_subjects',
            VERSION: 'cache_version'
        };
        
        this.init();
    }

    init() {
        console.log('📦 DataCacheManager initialized');
        this.checkVersion();
        this.cleanExpiredCache();
    }

    // ==================== Version Management ====================
    
    checkVersion() {
        const savedVersion = localStorage.getItem(this.cacheKeys.VERSION);
        if (savedVersion !== this.CACHE_VERSION) {
            console.log('🔄 Cache version mismatch, clearing cache');
            this.clearAll();
            localStorage.setItem(this.cacheKeys.VERSION, this.CACHE_VERSION);
        }
    }

    // ==================== Cache Operations ====================
    
    /**
     * حفظ بيانات في Cache
     */
    set(key, data) {
        try {
            const cacheItem = {
                data: data,
                timestamp: Date.now(),
                version: this.CACHE_VERSION
            };
            localStorage.setItem(key, JSON.stringify(cacheItem));
            console.log(`💾 Cached: ${key}`);
            return true;
        } catch (error) {
            console.error(`❌ Error caching ${key}:`, error);
            return false;
        }
    }

    /**
     * جلب بيانات من Cache
     */
    get(key, maxAge = this.CACHE_DURATION) {
        try {
            const item = localStorage.getItem(key);
            if (!item) {
                console.log(`📭 Cache miss: ${key}`);
                return null;
            }

            const cacheItem = JSON.parse(item);
            const age = Date.now() - cacheItem.timestamp;

            if (age > maxAge) {
                console.log(`⏰ Cache expired: ${key} (${Math.floor(age / 1000)}s old)`);
                localStorage.removeItem(key);
                return null;
            }

            console.log(`✅ Cache hit: ${key} (${Math.floor(age / 1000)}s old)`);
            return cacheItem.data;
        } catch (error) {
            console.error(`❌ Error reading cache ${key}:`, error);
            return null;
        }
    }

    /**
     * حذف عنصر محدد
     */
    remove(key) {
        localStorage.removeItem(key);
        console.log(`🗑️ Cache removed: ${key}`);
    }

    /**
     * مسح كل الـ Cache
     */
    clearAll() {
        Object.values(this.cacheKeys).forEach(key => {
            if (!key.endsWith('_')) {
                localStorage.removeItem(key);
            }
        });
        
        // مسح الشعب المخزنة
        Object.keys(localStorage).forEach(key => {
            if (key.startsWith(this.cacheKeys.SECTIONS)) {
                localStorage.removeItem(key);
            }
        });
        
        console.log('🧹 All cache cleared');
    }

    /**
     * تنظيف البيانات المنتهية
     */
    cleanExpiredCache() {
        let cleaned = 0;
        Object.keys(localStorage).forEach(key => {
            if (key.startsWith('cache_')) {
                if (!this.get(key)) {
                    cleaned++;
                }
            }
        });
        if (cleaned > 0) {
            console.log(`🧹 Cleaned ${cleaned} expired cache items`);
        }
    }

    // ==================== Specific Data Methods ====================

    /**
     * تحميل الصفوف
     */
    async getGrades(forceRefresh = false) {
        if (!forceRefresh) {
            const cached = this.get(this.cacheKeys.GRADES);
            if (cached) return cached;
        }

        try {
            console.log('🔄 Fetching grades from API...');
            const token = localStorage.getItem('access_token') || localStorage.getItem('token');
            const response = await fetch(`${this.API_BASE}/sections/my-grades/`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('API Error');

            const data = await response.json();
            this.set(this.cacheKeys.GRADES, data);
            return data;
        } catch (error) {
            console.error('❌ Error fetching grades:', error);
            // إرجاع البيانات القديمة إذا فشل التحميل
            return this.get(this.cacheKeys.GRADES, Infinity);
        }
    }

    /**
     * تحميل الشعب لصف معين
     */
    async getSections(gradeId, forceRefresh = false) {
        const key = this.cacheKeys.SECTIONS + gradeId;
        
        if (!forceRefresh) {
            const cached = this.get(key);
            if (cached) return cached;
        }

        try {
            console.log(`🔄 Fetching sections for grade ${gradeId}...`);
            const token = localStorage.getItem('access_token') || localStorage.getItem('token');
            const response = await fetch(`${this.API_BASE}/sections/grade/${gradeId}/sections/`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('API Error');

            const data = await response.json();
            this.set(key, data);
            return data;
        } catch (error) {
            console.error(`❌ Error fetching sections for grade ${gradeId}:`, error);
            return this.get(key, Infinity);
        }
    }

    /**
     * تحميل المشاريع
     */
    async getProjects(forceRefresh = false) {
        if (!forceRefresh) {
            const cached = this.get(this.cacheKeys.PROJECTS);
            if (cached) return cached;
        }

        try {
            console.log('🔄 Fetching projects from API...');
            const token = localStorage.getItem('access_token') || localStorage.getItem('token');
            const response = await fetch(`${this.API_BASE}/projects/`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error('API Error');

            const data = await response.json();
            this.set(this.cacheKeys.PROJECTS, data);
            return data;
        } catch (error) {
            console.error('❌ Error fetching projects:', error);
            return this.get(this.cacheKeys.PROJECTS, Infinity);
        }
    }

    /**
     * تحميل كل البيانات دفعة واحدة (عند الدخول للوحة التحكم)
     */
    async preloadAllData() {
        console.log('🚀 Preloading all data...');
        const startTime = Date.now();

        try {
            // تحميل متوازي لكل البيانات
            const [grades, projects] = await Promise.all([
                this.getGrades(true),
                this.getProjects(true)
            ]);

            // تحميل الشعب لكل صف
            if (grades && grades.grades) {
                const sectionsPromises = grades.grades.map(grade => 
                    this.getSections(grade.id, true)
                );
                await Promise.all(sectionsPromises);
            }

            const duration = Date.now() - startTime;
            console.log(`✅ All data preloaded in ${duration}ms`);
            
            return {
                success: true,
                duration: duration,
                grades: grades,
                projects: projects
            };
        } catch (error) {
            console.error('❌ Error preloading data:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * تحديث البيانات في الخلفية
     */
    async refreshInBackground() {
        console.log('🔄 Background refresh started...');
        setTimeout(() => {
            this.preloadAllData();
        }, 1000);
    }

    /**
     * الحصول على معلومات الـ Cache
     */
    getCacheInfo() {
        const info = {
            version: this.CACHE_VERSION,
            items: [],
            totalSize: 0
        };

        Object.keys(localStorage).forEach(key => {
            if (key.startsWith('cache_')) {
                const value = localStorage.getItem(key);
                const size = new Blob([value]).size;
                info.totalSize += size;
                
                try {
                    const item = JSON.parse(value);
                    const age = Date.now() - item.timestamp;
                    info.items.push({
                        key: key,
                        size: size,
                        age: Math.floor(age / 1000),
                        ageFormatted: this.formatDuration(age)
                    });
                } catch (e) {
                    // Skip invalid items
                }
            }
        });

        info.totalSizeFormatted = this.formatBytes(info.totalSize);
        return info;
    }

    // ==================== Helper Methods ====================

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    formatDuration(ms) {
        const seconds = Math.floor(ms / 1000);
        if (seconds < 60) return `${seconds}s`;
        const minutes = Math.floor(seconds / 60);
        return `${minutes}m ${seconds % 60}s`;
    }
}

// إنشاء instance عام
const dataCache = new DataCacheManager();

// Make it globally available
window.dataCache = dataCache;

console.log('✅ DataCacheManager loaded');
