import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import MainLayout from '../layouts/MainLayout.vue'
import PlanWeek from '../views/PlanWeek.vue'
import PlanMonth from '../views/PlanMonth.vue'
import RecurringTasks from '../views/RecurringTasks.vue'
import FocusTimer from '../views/FocusTimer.vue'
import Statistics from '../views/Statistics.vue'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login
    },
    {
        path: '/',
        component: MainLayout,
        meta: { requiresAuth: true },
        redirect: '/plan',
        children: [
            {
                path: 'plan',
                name: 'Plan',
                component: PlanWeek,
                meta: { title: '每日规划' }
            },
            {
                path: 'weekly',
                name: 'WeeklyPlan',
                component: PlanMonth,
                meta: { title: '每周规划' }
            },
            {
                path: 'recurring',
                name: 'RecurringTasks',
                component: RecurringTasks,
                meta: { title: '重复任务' }
            },
            {
                path: 'focus',
                name: 'FocusTimer',
                component: FocusTimer,
                meta: { title: '专注计时' }
            },
            {
                path: 'statistics',
                name: 'Statistics',
                component: Statistics,
                meta: { title: '复盘与统计' }
            }
        ]
    },
    {
        path: '/calendar',
        redirect: '/plan'
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    const user = localStorage.getItem('user')
    const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)

    if (requiresAuth && !user) {
        next('/login')
    } else if (to.path === '/login' && user) {
        next('/plan')
    } else {
        next()
    }
})

export default router
