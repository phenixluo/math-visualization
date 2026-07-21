<template>
  <div class="max-w-6xl mx-auto">
    <h2 class="text-2xl font-bold text-white mb-4 text-center">方程图形化</h2>

    <!-- 输入区域 -->
    <div class="flex justify-center gap-2 mb-4">
      <input
        v-model="equationInput"
        placeholder="输入方程，如 (9-x)+2=8"
        class="px-4 py-2 rounded-lg border border-gray-300 w-64 text-black"
        @keyup.enter="setEquation"
      />
      <button @click="setEquation" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
        设置方程
      </button>
    </div>

    <!-- 天平区域 -->
    <div ref="balanceAreaRef" class="relative h-[350px] bg-gradient-to-b from-slate-800 to-slate-900 rounded-xl overflow-hidden">
      <!-- 横梁 -->
      <div
        class="absolute left-1/2 top-[80px] h-2 bg-amber-700 origin-center transition-transform duration-700 ease-out"
        :style="{ width: `${beamWidth}px`, transform: `translateX(-50%) rotate(${beamAngleDeg}deg)` }"
      ></div>
      <!-- 支点 -->
      <div class="absolute left-1/2 top-[70px] w-0 h-0 border-l-[15px] border-r-[15px] border-t-[30px] border-l-transparent border-r-transparent border-t-amber-800 -translate-x-1/2"></div>

      <!-- 左侧绳子：连接横梁左端点和左托盘中心 -->
      <div
        class="absolute w-1 bg-amber-600 origin-top transition-all duration-700 ease-out"
        :style="leftRopeStyle"
      ></div>
      <!-- 右侧绳子：连接横梁右端点和右托盘中心 -->
      <div
        class="absolute w-1 bg-amber-600 origin-top transition-all duration-700 ease-out"
        :style="rightRopeStyle"
      ></div>

      <!-- 左侧托盘 -->
      <div
        class="absolute left-[80px] top-[160px] transition-transform duration-700 ease-out"
        :style="{ transform: `translateY(${-Math.sin(beamAngleRad) * 180}px)` }"
      >
        <div
          class="w-[300px] min-h-[100px] bg-gradient-to-b from-blue-100 to-blue-200 border-2 border-blue-400 rounded-lg p-3 cursor-pointer hover:ring-2 hover:ring-blue-300"
          :class="{ 'ring-4 ring-blue-400': selectedWeight && targetSide === 'left' }"
          @click="handleTrayClick('left')"
        >
          <div class="text-xs text-blue-600 font-bold mb-1 text-center">左边（点击添加）</div>
          <Transition name="expr" mode="out-in">
            <div :key="leftExpr" class="text-xl font-mono font-bold text-blue-800 text-center">
              {{ leftExpr || '0' }}
            </div>
          </Transition>
        </div>
      </div>

      <!-- 右侧托盘 -->
      <div
        class="absolute right-[80px] top-[160px] transition-transform duration-700 ease-out"
        :style="{ transform: `translateY(${Math.sin(beamAngleRad) * 180}px)` }"
      >
        <div
          class="w-[300px] min-h-[100px] bg-gradient-to-b from-red-100 to-red-200 border-2 border-red-400 rounded-lg p-3 cursor-pointer hover:ring-2 hover:ring-red-300"
          :class="{ 'ring-4 ring-red-400': selectedWeight && targetSide === 'right' }"
          @click="handleTrayClick('right')"
        >
          <div class="text-xs text-red-600 font-bold mb-1 text-center">右边（点击添加）</div>
          <Transition name="expr" mode="out-in">
            <div :key="rightExpr" class="text-xl font-mono font-bold text-red-800 text-center">
              {{ rightExpr || '0' }}
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- 砝码选择区 -->
    <div class="mt-6 grid grid-cols-4 gap-4">
      <div class="bg-green-100 rounded-lg p-3">
        <div class="text-green-700 font-bold text-center mb-2">+ 加号组</div>
        <div class="flex flex-wrap gap-2 justify-center">
          <button
            v-for="w in plusWeights"
            :key="w"
            @click="selectWeight('plus', w)"
            :class="['w-10 h-10 rounded-full font-bold transition', selectedWeight?.group === 'plus' && selectedWeight?.value === w ? 'bg-green-700 text-white ring-2 ring-white' : 'bg-green-500 text-white hover:bg-green-600']"
          >+{{ w }}</button>
        </div>
      </div>
      <div class="bg-red-100 rounded-lg p-3">
        <div class="text-red-700 font-bold text-center mb-2">- 减号组</div>
        <div class="flex flex-wrap gap-2 justify-center">
          <button
            v-for="w in minusWeights"
            :key="w"
            @click="selectWeight('minus', w)"
            :class="['w-10 h-10 rounded-full font-bold transition', selectedWeight?.group === 'minus' && selectedWeight?.value === w ? 'bg-red-700 text-white ring-2 ring-white' : 'bg-red-500 text-white hover:bg-red-600']"
          >-{{ w }}</button>
        </div>
      </div>
      <div class="bg-yellow-100 rounded-lg p-3">
        <div class="text-yellow-700 font-bold text-center mb-2">× 乘号组</div>
        <div class="flex flex-wrap gap-2 justify-center">
          <button
            v-for="w in multiplyWeights"
            :key="w"
            @click="selectWeight('multiply', w)"
            :class="['w-10 h-10 rounded-full font-bold transition', selectedWeight?.group === 'multiply' && selectedWeight?.value === w ? 'bg-yellow-700 text-white ring-2 ring-white' : 'bg-yellow-500 text-white hover:bg-yellow-600']"
          >×{{ w }}</button>
        </div>
      </div>
      <div class="bg-purple-100 rounded-lg p-3">
        <div class="text-purple-700 font-bold text-center mb-2">÷ 除号组</div>
        <div class="flex flex-wrap gap-2 justify-center">
          <button
            v-for="w in divideWeights"
            :key="w"
            @click="selectWeight('divide', w)"
            :class="['w-10 h-10 rounded-full font-bold transition', selectedWeight?.group === 'divide' && selectedWeight?.value === w ? 'bg-purple-700 text-white ring-2 ring-white' : 'bg-purple-500 text-white hover:bg-purple-600']"
          >÷{{ w }}</button>
        </div>
      </div>
    </div>

    <!-- 操作提示 -->
    <div class="mt-4 text-center text-white text-sm">
      <span v-if="selectedWeight">已选择：{{ selectedWeight.label }}，点击左边或右边秤盘添加</span>
      <span v-else>请先点击下方砝码，然后点击天平秤盘</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as mathjs from 'mathjs'

// ============ 状态 ============
const equationInput = ref('(9-x)+2=8')
const leftExpr = ref('')
const rightExpr = ref('')
const selectedWeight = ref(null)
const targetSide = ref(null)

// 初始方程的解，用于计算天平倾斜（固定 x 值）
const initialX = ref(0)

// 天平区域引用和动态容器宽度
const balanceAreaRef = ref(null)
const containerWidth = ref(1152)

// 横梁配置
const beamWidth = 640
const halfBeam = beamWidth / 2

function updateContainerWidth() {
  if (balanceAreaRef.value) {
    containerWidth.value = balanceAreaRef.value.offsetWidth
  }
}

let resizeObserver = null
onMounted(() => {
  updateContainerWidth()
  resizeObserver = new ResizeObserver(updateContainerWidth)
  if (balanceAreaRef.value) {
    resizeObserver.observe(balanceAreaRef.value)
  }
})
onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})

const plusWeights = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'x']
const minusWeights = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'x']
const multiplyWeights = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'x']
const divideWeights = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'x']

// ============ 计算属性 ============
// 使用固定的 initialX 计算两边重量，判断天平倾斜
// 这样添加砝码后可以看到是否平衡，而不是重新解方程
const beamAngleDeg = computed(() => {
  const left = leftExpr.value
  const right = rightExpr.value

  if (!left || !right) return 0

  console.log(`beamAngle: x=${initialX.value}, left="${left}", right="${right}"`)

  try {
    const leftNormalized = left.replace(/×/g, '*').replace(/÷/g, '/')
    const rightNormalized = right.replace(/×/g, '*').replace(/÷/g, '/')

    console.log(`beamAngle: normalized left="${leftNormalized}", right="${rightNormalized}"`)

    const leftEval = mathjs.evaluate(leftNormalized, { x: initialX.value })
    const rightEval = mathjs.evaluate(rightNormalized, { x: initialX.value })
    
    const leftWeight = parseFloat(mathjs.number(leftEval))
    const rightWeight = parseFloat(mathjs.number(rightEval))

    console.log(`beamAngle: leftWeight=${leftWeight}, rightWeight=${rightWeight}`)

    if (!isNaN(leftWeight) && !isNaN(rightWeight)) {
        const diff = rightWeight - leftWeight
        return Math.max(-15, Math.min(15, diff * 2))
      }
    } catch (e) {
      // 计算失败，使用线性近似
      const leftVal = evaluateExpr(left)
      const rightVal = evaluateExpr(right)

      const leftWeight = leftVal.xCoeff * initialX.value + leftVal.constant
      const rightWeight = rightVal.xCoeff * initialX.value + rightVal.constant
      const diff = rightWeight - leftWeight

      return Math.max(-15, Math.min(15, diff * 3))
    }

    return 0
  })

  const beamAngleRad = computed(() => beamAngleDeg.value * Math.PI / 180)

  const leftRopeStyle = computed(() => {
    const angle = beamAngleRad.value
    const cw = containerWidth.value
    const centerXpx = cw / 2

    // 横梁中心线 Y = 80 + 1 = 81px
    const beamCenterY = 81
    // 横梁左端点
    const beamLeftX = centerXpx - halfBeam * Math.cos(angle)
    const beamLeftY = beamCenterY - halfBeam * Math.sin(angle)

    // 左托盘中心
    const trayCenterX = 230
    const trayCenterY = 210 - Math.sin(angle) * 180

    const dx = trayCenterX - beamLeftX
    const dy = trayCenterY - beamLeftY
    const length = Math.sqrt(dx * dx + dy * dy)
    const ropeAngle = Math.atan2(dy, dx) * 180 / Math.PI - 90

    return {
      left: `${beamLeftX}px`,
      top: `${beamLeftY}px`,
      height: `${length}px`,
      transform: `rotate(${ropeAngle}deg)`
    }
  })

  const rightRopeStyle = computed(() => {
    const angle = beamAngleRad.value
    const cw = containerWidth.value
    const centerXpx = cw / 2

    // 横梁中心线 Y = 81px
    const beamCenterY = 81
    // 横梁右端点
    const beamRightX = centerXpx + halfBeam * Math.cos(angle)
    const beamRightY = beamCenterY + halfBeam * Math.sin(angle)

    // 右托盘中心
    const trayCenterX = cw - 230
    const trayCenterY = 210 + Math.sin(angle) * 180

    const dx = trayCenterX - beamRightX
    const dy = trayCenterY - beamRightY
    const length = Math.sqrt(dx * dx + dy * dy)
    const ropeAngle = Math.atan2(dy, dx) * 180 / Math.PI - 90

    return {
      left: `${beamRightX}px`,
      top: `${beamRightY}px`,
      height: `${length}px`,
      transform: `rotate(${ropeAngle}deg)`
    }
  })

  // ============ 方法 ============
function setEquation() {
  const eq = equationInput.value.trim()
  const parts = eq.split('=')
  if (parts.length !== 2) return

  leftExpr.value = parts[0].trim()
  rightExpr.value = parts[1].trim()

  // 计算初始方程的解
  try {
    const leftExprStr = parts[0].trim().replace(/×/g, '*').replace(/÷/g, '/')
    const rightExprStr = parts[1].trim().replace(/×/g, '*').replace(/÷/g, '/')

    // 使用二分法求解方程 f(x) = left - right = 0
    const f = (x) => {
      try {
        const leftVal = parseFloat(mathjs.evaluate(leftExprStr, { x }))
        const rightVal = parseFloat(mathjs.evaluate(rightExprStr, { x }))
        if (isNaN(leftVal) || isNaN(rightVal)) return NaN
        return leftVal - rightVal
      } catch (e) {
        return NaN
      }
    }

    // 在多个区间搜索，避免奇点（如 x=0）
    const intervals = [
      [-1000, -0.001],
      [0.001, 1000]
    ]

    let mid = 0
    let found = false

    for (const [start, end] of intervals) {
      let left = start
      let right = end
      for (let i = 0; i < 50; i++) {
        mid = (left + right) / 2
        const fMid = f(mid)
        const fLeft = f(left)
        
        if (isNaN(fMid) || isNaN(fLeft)) break
        
        if (Math.abs(fMid) < 0.0001) {
          found = true
          break
        }
        
        if (fMid * fLeft < 0) {
          right = mid
        } else {
          left = mid
        }
      }
      if (found) break
    }

    // 如果二分法结果不好或没找到，使用线性方法
    if (!found || isNaN(mid) || Math.abs(f(mid)) > 1) {
      const leftVal = evaluateExpr(leftExprStr)
      const rightVal = evaluateExpr(rightExprStr)
      if (leftVal.xCoeff !== rightVal.xCoeff) {
        const denom = leftVal.xCoeff - rightVal.xCoeff
        if (denom !== 0) {
          mid = (rightVal.constant - leftVal.constant) / denom
        }
      }
    }

    if (!isNaN(mid)) {
      initialX.value = mid
    }
  } catch (e) {
    // 全部失败，使用线性方法
    const leftParts = parts[0].trim().replace(/×/g, '*').replace(/÷/g, '/')
    const rightParts = parts[1].trim().replace(/×/g, '*').replace(/÷/g, '/')
    try {
      const leftVal = evaluateExpr(leftParts)
      const rightVal = evaluateExpr(rightParts)
      if (leftVal.xCoeff !== rightVal.xCoeff) {
        const denom = leftVal.xCoeff - rightVal.xCoeff
        if (denom !== 0) {
          initialX.value = (rightVal.constant - leftVal.constant) / denom
        }
      }
    } catch (e2) {
      // 保持默认 x=0
    }
  }
}

function selectWeight(group, value) {
  const opMap = { plus: '+', minus: '-', multiply: '*', divide: '/' }
  selectedWeight.value = { group, value, label: `${opMap[group]}${value}` }
}

function handleTrayClick(side) {
  if (!selectedWeight.value) return

  targetSide.value = side
  const weight = selectedWeight.value
  const opMap = { plus: '+', minus: '-', multiply: '*', divide: '/' }
  const op = opMap[weight.group]

  // 添加砝码到对应侧
  if (side === 'left') {
    leftExpr.value = simplify(`${leftExpr.value}${op}${weight.value}`)
  } else {
    rightExpr.value = simplify(`${rightExpr.value}${op}${weight.value}`)
  }

  // 清除选择
  selectedWeight.value = null
}

// 简化表达式
// 使用 mathjs 计算表达式，保留 x 变量
function simplify(expr) {
  if (!expr) return '0'

  // 替换运算符：× → *, ÷ → /
  const normalized = expr.replace(/×/g, '*').replace(/÷/g, '/')

  // 使用 mathjs 简化表达式
  try {
    const result = mathjs.simplify(normalized)
    let str = result.toString()

    // 替换回显示格式：* → ×, / → ÷
    str = str.replace(/\*/g, '×').replace(/\//g, '÷')

    // 处理负号格式：-1x → -x, -1 → -1
    str = str.replace(/(-?)\d+x/g, (match, sign) => {
      const num = parseInt(match.replace('x', ''))
      if (num === 1) return 'x'
      if (num === -1) return '-x'
      return match
    })

    // 处理括号消失：(x) → x
    str = str.replace(/^\(([^()]+)\)$/, '$1')

    // 处理格式：1x → x, 0+x → x, 0-x → -x
    str = str.replace(/1x/g, 'x')
    str = str.replace(/^0\+/, '')
    str = str.replace(/^0\-/, '-')

    return str || '0'
  } catch (e) {
    return expr
  }
}

// 评估表达式（求 x 系数和常数）
// 使用 mathjs 解析表达式
function evaluateExpr(expr) {
  if (!expr) return { xCoeff: 0, constant: 0 }

  const normalized = expr.replace(/×/g, '*').replace(/÷/g, '/')

  try {
    const node = mathjs.parse(normalized)

    // 提取常数项和 x 系数
    let constant = 0
    let xCoeff = 0

    // 使用 evaluate 代入不同 x 值来求解系数
    // f(x) = a*x + b
    // f(0) = b
    // f(1) - f(0) = a
    const f0 = mathjs.evaluate(normalized, { x: 0 })
    const f1 = mathjs.evaluate(normalized, { x: 1 })

    constant = parseFloat(f0) || 0
    xCoeff = parseFloat(f1 - f0) || 0

    // 处理 NaN 情况
    if (isNaN(constant)) constant = 0
    if (isNaN(xCoeff)) xCoeff = 0

    return { xCoeff, constant }
  } catch (e) {
    return { xCoeff: 0, constant: 0 }
  }
}

// 初始化
setEquation()
</script>

<style scoped>
.expr-enter-active,
.expr-leave-active {
  transition: all 0.4s ease;
}
.expr-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(-10px);
}
.expr-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(10px);
}
</style>
