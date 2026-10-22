import iconMon from '../image/1.png'
import iconTue from '../image/2.png'
import iconWed from '../image/3.png'
import iconThu from '../image/4.png'
import iconFri from '../image/5.png'
import iconSat from '../image/6.png'
import iconSun from '../image/7.png'

const WEEK_LABELS = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
/** 按 getDay() 索引：0=周日 … 6=周六 */
const DAY_ICON_IMAGES = [iconSun, iconMon, iconTue, iconWed, iconThu, iconFri, iconSat]

export function formatDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export function parseDate(dateStr) {
  const [y, m, d] = dateStr.split('-').map(Number)
  return new Date(y, m - 1, d)
}

/** 返回该日期所在周的周一（YYYY-MM-DD） */
export function getMonday(date = new Date()) {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  const day = d.getDay()
  const diff = day === 0 ? -6 : 1 - day
  d.setDate(d.getDate() + diff)
  return formatDate(d)
}

export function addDays(dateStr, days) {
  const d = parseDate(dateStr)
  d.setDate(d.getDate() + days)
  return formatDate(d)
}

export function getWeekDays(weekStart) {
  const today = formatDate(new Date())
  const days = []
  for (let i = 0; i < 7; i++) {
    const date = addDays(weekStart, i)
    const d = parseDate(date)
    const dayIndex = d.getDay()
    days.push({
      date,
      weekdayLabel: WEEK_LABELS[dayIndex],
      iconImage: DAY_ICON_IMAGES[dayIndex],
      dateNum: d.getDate(),
      month: d.getMonth() + 1,
      isToday: date === today
    })
  }
  return days
}

export function getWeekRangeText(weekStart) {
  const start = parseDate(weekStart)
  const end = parseDate(addDays(weekStart, 6))
  return `${start.getFullYear()}年${start.getMonth() + 1}月${start.getDate()}日 – ${end.getMonth() + 1}月${end.getDate()}日`
}

/** 返回某月内与该月有交集的全部自然周（周一至周日） */
export function getMonthWeeks(year, month) {
  const firstOfMonth = new Date(year, month - 1, 1)
  const lastOfMonth = new Date(year, month, 0)
  lastOfMonth.setHours(0, 0, 0, 0)

  let current = getMonday(firstOfMonth)
  const todayMonday = getMonday(new Date())
  const weeks = []
  let index = 1

  while (parseDate(current) <= lastOfMonth) {
    const weekEnd = addDays(current, 6)
    if (parseDate(weekEnd) >= firstOfMonth) {
      const start = parseDate(current)
      const end = parseDate(weekEnd)
      weeks.push({
        weekStart: current,
        weekEnd,
        index,
        label: `第${index}周`,
        rangeText: `${start.getMonth() + 1}/${start.getDate()} – ${end.getMonth() + 1}/${end.getDate()}`,
        isCurrentWeek: current === todayMonday
      })
      index += 1
    }
    current = addDays(current, 7)
  }
  return weeks
}

export function getMonthTitle(year, month) {
  return `${year}年${month}月`
}

/** 某周是否已全部过去（周日 < 今天） */
export function isWeekPast(weekStart) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return parseDate(addDays(weekStart, 6)) < today
}
