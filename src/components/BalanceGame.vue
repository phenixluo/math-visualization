<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
    <div class="max-w-5xl mx-auto">
      <h2 class="text-3xl font-bold text-center text-gray-800 mb-2">方程图形化</h2>
      <p class="text-center text-gray-600 mb-6">通过天平理解等式两边相等的关系，学会解方程</p>
      
      <!-- 模式选择 -->
      <div class="flex justify-center gap-4 mb-6">
        <button 
          @click="mode = 'explore'"
          class="px-6 py-2 rounded-lg font-medium transition-all"
          :class="mode === 'explore' ? 'bg-purple-600 text-white shadow-lg' : 'bg-white text-gray-700 hover:bg-gray-100'"
        >
          探索模式
        </button>
        <button 
          @click="setChallengeMode"
          class="px-6 py-2 rounded-lg font-medium transition-all"
          :class="mode === 'challenge' ? 'bg-purple-600 text-white shadow-lg' : 'bg-white text-gray-700 hover:bg-gray-100'"
        >
          挑战模式
        </button>
      </div>
      
      <!-- 挑战模式 -->
      <div v-if="mode === 'challenge' && challengeEquation" class="text-center mb-6">
        <div class="inline-block bg-purple-100 border-2 border-purple-400 rounded-xl px-8 py-4">
          <div class="text-sm text-purple-600 mb-1">目标方程</div>
          <div class="text-2xl font-bold text-purple-800">{{ challengeEquation.left }} = {{ challengeEquation.right }}</div>
          <div class="text-sm text-purple-600 mt-2">拖动砝码使天平平衡，然后告诉我 x = ?</div>
        </div>
        <div class="mt-4">
          <span class="text-gray-600">你的答案：</span>
          <span class="font-bold text-gray-800">x = </span>
          <input 
            v-model.number="studentAnswer" 
            type="number" 
            class="w-16 px-2 py-1 border-2 border-purple-300 rounded-lg text-center font-bold text-lg"
            placeholder="?"
          />
          <button 
            @click="checkAnswer"
            class="ml-3 px-4 py-1 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            检查答案
          </button>
          <span v-if="answerFeedback" class="ml-3 font-bold" :class="answerFeedback === '正确！' ? 'text-green-600' : 'text-red-600'">
            {{ answerFeedback }}
          </span>
        </div>
      </div>
      
      <!-- 天平区域 -->
      <div class="balance-area bg-white rounded-2xl shadow-lg p-6 mb-6">
        <div class="balance-stand relative h-72 flex items-end justify-center">

          <div class="pillar absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-40 bg-gradient-to-t from-amber-700 to-amber-500 rounded-t-lg"></div>
          <div class="base absolute bottom-0 left-1/2 -translate-x-1/2 w-32 h-5 bg-gradient-to-t from-amber-800 to-amber-600 rounded-lg shadow-md"></div>

          <!-- 旋转视觉部分（仅视觉效果） -->
          <div
            class="beam-rotate absolute pointer-events-none"
            :style="{ bottom: '160px', left: '50%', transform: `translateX(-50%) rotate(${beamAngle}deg)`, transformOrigin: 'center center' }"
          >
            <div class="beam relative w-[500px] h-3 bg-gradient-to-r from-amber-700 via-amber-600 to-amber-700 rounded-full shadow-lg">
              <!-- 支点 -->
              <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-amber-900 border-4 border-amber-500 flex items-center justify-center">
                <span class="text-white text-sm font-bold">=</span>
              </div>
            </div>
          </div>

          <!-- 左侧托盘（随倾斜上下移动） -->
          <div 
            class="absolute" 
            :style="{ 
              left: 'calc(50% - 250px)', 
              top: `${180 - Math.sin(beamAngle * Math.PI / 180) * 250}px`,
              transition: 'top 0.5s ease-in-out'
            }"
          >
            <!-- 左侧绳子（连接横梁和托盘） -->
            <div class="absolute left-1/2 -translate-x-1/2 w-0.5 bg-amber-800"
                 :style="{ 
                   height: '52px',
                   top: '-52px',
                   transition: 'height 0.5s ease-in-out'
                 }">
            </div>
            <div
              class="tray w-48 min-h-24 bg-gradient-to-b from-gray-100 to-gray-200 border-2 border-gray-400 rounded-lg shadow-md p-2 flex flex-wrap gap-1 justify-center items-center content-start drop-zone cursor-pointer"
              :class="{ 'ring-4 ring-blue-400 bg-blue-50 scale-105': isDragOver === 'left' }"
              @click="handleTrayClick('left')"
              @mouseenter="isDragOver = selectedWeight ? 'left' : null"
              @mouseleave="isDragOver = null"
            >
              <TransitionGroup name="token" tag="div" class="flex flex-wrap gap-1">
              <div
                v-for="(token, idx) in leftRawTokensDisplay"
                :key="token.id"
                class="weight-chip"
                :class="getChipClass(token)"
                @click.stop="removeFromTray('left', idx)"
                :title="'点击删除 ' + token.display"
              >
                <span class="font-mono font-bold">{{ token.display }}</span>
              </div>
            </TransitionGroup>
            <div v-if="leftRawTokensDisplay.length === 0" class="text-gray-400 text-xs w-full text-center py-3">
              点击添加
            </div>
            </div>
            <div class="mt-2 text-center font-mono text-sm bg-blue-50 rounded px-2 py-1">
              <span class="text-xs text-gray-500">化简：</span>
              <span class="font-bold text-blue-700">{{ leftSimplified || '0' }}</span>
              <span class="text-xs text-gray-500 ml-1">常数={{ leftConstant }}</span>
            </div>
          </div>

          <!-- 右侧托盘（随倾斜上下移动） -->
          <div 
            class="absolute" 
            :style="{ 
              right: 'calc(50% - 250px)', 
              top: `${180 + Math.sin(beamAngle * Math.PI / 180) * 250}px`,
              transition: 'top 0.5s ease-in-out'
            }"
          >
            <!-- 右侧绳子（连接横梁和托盘） -->
            <div class="absolute left-1/2 -translate-x-1/2 w-0.5 bg-amber-800"
                 :style="{ 
                   height: '52px',
                   top: '-52px',
                   transition: 'height 0.5s ease-in-out'
                 }">
            </div>
            <div
              class="tray w-48 min-h-24 bg-gradient-to-b from-gray-100 to-gray-200 border-2 border-gray-400 rounded-lg shadow-md p-2 flex flex-wrap gap-1 justify-center items-center content-start drop-zone cursor-pointer"
              :class="{ 'ring-4 ring-red-400 bg-red-50 scale-105': isDragOver === 'right' }"
              @click="handleTrayClick('right')"
              @mouseenter="isDragOver = selectedWeight ? 'right' : null"
              @mouseleave="isDragOver = null"
            >
              <TransitionGroup name="token" tag="div" class="flex flex-wrap gap-1">
              <div
                v-for="(token, idx) in rightRawTokensDisplay"
                :key="token.id"
                class="weight-chip"
                :class="getChipClass(token)"
                @click.stop="removeFromTray('right', idx)"
                :title="'点击删除 ' + token.display"
              >
                <span class="font-mono font-bold">{{ token.display }}</span>
              </div>
            </TransitionGroup>
            <div v-if="rightRawTokensDisplay.length === 0" class="text-gray-400 text-xs w-full text-center py-3">
              点击添加
            </div>
            </div>
            <div class="mt-2 text-center font-mono text-sm bg-red-50 rounded px-2 py-1">
              <span class="text-xs text-gray-500">化简：</span>
              <span class="font-bold text-red-700">{{ rightSimplified || '0' }}</span>
              <span class="text-xs text-gray-500 ml-1">常数={{ rightConstant }}</span>
            </div>
          </div>
        </div>
        
        <!-- 等式显示 -->
        <div class="mt-8 flex justify-center items-center gap-4 text-xl font-mono">
          <div class="px-4 py-2 bg-blue-50 rounded-lg">
            <span class="font-bold text-blue-700">{{ leftSimplified || '0' }}</span>
          </div>
          <div class="text-2xl font-bold text-gray-400">=</div>
          <div class="px-4 py-2 bg-red-50 rounded-lg">
            <span class="font-bold text-red-700">{{ rightSimplified || '0' }}</span>
          </div>
        </div>
        
        <!-- 操作提示 -->
        <div v-if="stepHint" class="mt-4 text-center">
          <div class="inline-block bg-amber-100 border border-amber-400 rounded-lg px-6 py-3 text-amber-900">
            <div class="text-lg font-bold mb-1">📐 提示</div>
            <div class="text-sm">{{ stepHint }}</div>
          </div>
        </div>
        
        <!-- 解方程成功 -->
        <div v-if="showXResult && solvedX !== null" class="mt-4 text-center">
          <div class="inline-block bg-green-100 border-2 border-green-400 rounded-xl px-6 py-3">
            <div class="text-green-700 text-lg">
              🎉 解方程成功！<br/>
              <span class="text-3xl font-bold">x = {{ solvedX }}</span>
            </div>
            <div class="text-green-600 text-sm mt-2">
              验证：{{ leftSimplified }} = {{ rightSimplified }} = {{ solvedX }}
            </div>
          </div>
        </div>
        
        <!-- 方程输入区 -->
        <div class="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4 border border-blue-200">
          <div class="flex items-center justify-center gap-4">
            <label class="text-gray-700 font-medium">输入方程：</label>
            <input
              v-model="inputEquation"
              type="text"
              placeholder="例如: 3 - x = 2"
              class="px-4 py-2 border-2 border-blue-300 rounded-lg font-mono text-lg w-64 focus:outline-none focus:border-purple-500"
              @keyup.enter="parseEquation"
            />
            <button
              @click="parseEquation"
              class="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
            >
              解析方程
            </button>
          </div>
          <div v-if="equationError" class="mt-2 text-center text-red-500 text-sm">
            {{ equationError }}
          </div>
          <div v-if="inputEquation && !equationError" class="mt-2 text-center text-gray-600 text-sm">
            💡 输入格式：左边表达式 = 右边表达式（支持 x、数字、+-*/）
          </div>
        </div>
        
      </div>
      
      <!-- 砝码区域 -->
      <div class="weights-area bg-white rounded-2xl shadow-lg p-5">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-800">砝码区 <span class="text-sm text-gray-500 font-normal">（点击选择砝码，然后点击天平托盘添加）</span></h3>
          <button
            @click="resetAll"
            class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors text-sm"
          >
            重置
          </button>
        </div>

        <div class="mb-3 text-center text-sm text-gray-600">
          <span v-if="selectedWeight">
            <span class="font-bold text-purple-600">已选择：{{ selectedWeight }}</span>
            <span class="ml-2">→ 点击天平托盘添加</span>
          </span>
          <span v-else>请选择一个砝码</span>
        </div>

        <div class="flex flex-col gap-4">
          <div 
            v-for="(group, gIdx) in weightGroups" 
            :key="gIdx" 
            class="p-4 rounded-xl border-2"
            :class="getGroupClass(group.color)"
          >
            <div class="flex items-center mb-3">
              <span class="text-sm font-semibold px-3 py-1 rounded-full" :class="[getGroupTitleClass(group.color), getGroupBadgeBg(group.color)]">
                {{ group.label }}
              </span>
            </div>
            <div class="flex flex-wrap gap-3">
              <div
                v-for="(weight, idx) in group.weights"
                :key="idx"
                class="weight-chip cursor-pointer px-4 py-2 transition-all duration-200"
                :class="selectedWeight === weight ? 'bg-yellow-300 text-yellow-900 border-2 border-yellow-600 scale-110 shadow-lg' : [getChipClass(weight), 'hover:scale-105']"
                @click="selectWeight(weight)"
                :title="'选择 ' + weight"
              >
                <span class="font-mono font-bold text-sm">{{ weight }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="mt-4 p-3 bg-purple-50 rounded-lg border border-purple-200">
          <p class="text-sm text-gray-700">
            <span class="font-semibold text-purple-800">💡 解方程规则：</span><br/>
            1. x 和 -x 在同一托盘相遇会互相抵消消失<br/>
            2. 天平倾斜程度由两边的<strong>常数项差值</strong>决定<br/>
            3. 两边都含 x 时天平保持平衡（因为不知道 x 多大）<br/>
            4. 当一边只剩 x，另一边只剩数字时，x 的值就出来了！
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const weightGroups = [
  { op: '+', label: '加法砝码', color: 'green', weights: ['+x', '+0', '+1', '+2', '+3', '+4', '+5', '+6', '+7', '+8', '+9'] },
  { op: '-', label: '减法砝码', color: 'red', weights: ['-x', '-0', '-1', '-2', '-3', '-4', '-5', '-6', '-7', '-8', '-9'] },
  { op: '*', label: '乘法砝码', color: 'blue', weights: ['*x', '*0', '*1', '*2', '*3', '*4', '*5', '*6', '*7', '*8', '*9'] },
  { op: '/', label: '除法砝码', color: 'orange', weights: ['/x', '/0', '/1', '/2', '/3', '/4', '/5', '/6', '/7', '/8', '/9'] }
]

const weights = weightGroups.flatMap(g => g.weights)

const leftRawTokens = ref([])  // 原始输入顺序
const rightRawTokens = ref([])
const isDragOver = ref(null)
const selectedWeight = ref(null)
const mode = ref('explore')
const studentAnswer = ref(null)
const answerFeedback = ref('')
const challengeEquation = ref(null)
const showXResult = ref(false)
const inputEquation = ref('')
const equationError = ref('')
const solvedXValue = ref(null)  // 存储从方程中计算出的真实x值（不显示）

// 选择砝码
const selectWeight = (weight) => {
  if (selectedWeight.value === weight) {
    selectedWeight.value = null  // 再次点击取消选择
  } else {
    selectedWeight.value = weight
  }
}

// 将带运算符前缀的砝码转换为标准 tokens
const parseWeightToTokens = (weight) => {
  if (typeof weight !== 'string') return [weight]
  
  if (weight.startsWith('+')) {
    const val = weight.substring(1)
    if (val === '0') return []
    return ['+', val]
  }
  
  if (weight.startsWith('-')) {
    const val = weight.substring(1)
    if (val === '0') return []
    return ['-', val]
  }
  
  if (weight.startsWith('*')) {
    const val = weight.substring(1)
    if (val === '0') return []
    return ['*', val]
  }
  
  if (weight.startsWith('/')) {
    const val = weight.substring(1)
    return ['/', val]
  }
  
  return [weight]
}

// 判断是否需要用括号包裹
const needsParenWrap = (tokens) => {
  if (tokens.length < 2) return false
  if (tokens[0] === '(' && tokens[tokens.length - 1] === ')') return false
  return tokens.some(t => t === '+' || t === '-')
}

// 点击托盘添加砝码
const handleTrayClick = (side) => {
  if (!selectedWeight.value) return
  const weight = selectedWeight.value
  const tokens = parseWeightToTokens(weight)
  if (tokens.length === 0) return

  const targetTokens = side === 'left' ? leftRawTokens.value : rightRawTokens.value

  // 如果添加的是乘除运算符，且当前托盘有加减表达式，自动添加括号
  if (tokens.length > 0 && (tokens[0] === '*' || tokens[0] === '/')) {
    if (targetTokens.length > 0 && needsParenWrap(targetTokens)) {
      const wrapped = ['(', ...targetTokens, ')']
      if (side === 'left') {
        leftRawTokens.value = [...wrapped, ...tokens]
      } else {
        rightRawTokens.value = [...wrapped, ...tokens]
      }
      return
    }
  }

  if (side === 'left') {
    leftRawTokens.value = [...leftRawTokens.value, ...tokens]
  } else {
    rightRawTokens.value = [...rightRawTokens.value, ...tokens]
  }
}

// 括号相关辅助函数
const findMatchingParen = (tokens, startIdx) => {
  let depth = 1
  for (let i = startIdx + 1; i < tokens.length; i++) {
    if (tokens[i] === '(') depth++
    if (tokens[i] === ')') depth--
    if (depth === 0) return i
  }
  return -1
}

const removeOuterParens = (tokens) => {
  if (tokens.length < 3 || tokens[0] !== '(' || tokens[tokens.length - 1] !== ')') {
    return tokens
  }
  let depth = 0
  for (let i = 0; i < tokens.length; i++) {
    if (tokens[i] === '(') depth++
    if (tokens[i] === ')') depth--
    if (depth === 0 && i < tokens.length - 1) {
      return tokens
    }
  }
  return tokens.slice(1, -1)
}

const evaluateGroup = (tokens) => {
  let xCount = 0
  let constant = 0
  let sign = 1
  for (let j = 0; j < tokens.length; j++) {
    const t = tokens[j]
    if (t === '+') { sign = 1; continue }
    if (t === '-') { sign = -1; continue }
    const parsed = parseToken(t)
    if (parsed.type === 'x') {
      xCount += sign * parsed.coeff
    } else if (parsed.type === 'num') {
      constant += sign * parsed.num
    }
    sign = 1
  }
  return { xCount, constant }
}

const processParenCancel = (tokens) => {
  const result = []
  let i = 0
  while (i < tokens.length) {
    const t = tokens[i]
    if (t === '(') {
      const endIdx = findMatchingParen(tokens, i)
      if (endIdx !== -1) {
        const groupTokens = tokens.slice(i + 1, endIdx)
        const groupValue = evaluateGroup(groupTokens)
        // 检查前一个项是否可抵消
        if (result.length > 0) {
          const prev = result[result.length - 1]
          const prevParsed = parseToken(prev)
          if (groupValue.xCount === 0 && prevParsed.type === 'num') {
            if (prevParsed.num + groupValue.constant === 0) {
              result.pop()
              i = endIdx + 1
              continue
            }
          }
        }
        // 检查后一个项是否可抵消
        if (endIdx + 1 < tokens.length) {
          const next = tokens[endIdx + 1]
          const nextParsed = parseToken(next)
          if (groupValue.xCount === 0 && nextParsed.type === 'num') {
            if (groupValue.constant + nextParsed.num === 0) {
              i = endIdx + 2
              continue
            }
          }
        }
        result.push(t)
        i++
      } else {
        result.push(t)
        i++
      }
    } else {
      result.push(t)
      i++
    }
  }
  return result
}

// 处理加减抵消和计算（如 8-2 → 6，2-2 → 消失，6+x-6 → x）
// 注意：不处理括号内的内容，只处理括号外的运算
const processAddSubCancel = (tokens) => {
  if (tokens.length === 0) return tokens

  const result = [...tokens]

  // 扫描表达式，只处理括号外的运算
  let changed = true
  while (changed) {
    changed = false

    // 第一趟：处理相邻的同类型项（数字和数字，x和x）
    for (let i = 0; i < result.length; i++) {
      const op = result[i]
      if (op !== '+' && op !== '-') continue

      // 检查是否在括号内（跳过括号内的运算）
      let depth = 0
      for (let j = 0; j < i; j++) {
        if (result[j] === '(') depth++
        if (result[j] === ')') depth--
      }
      if (depth > 0) continue

      // 检查两边是否都是数字或x项
      if (i > 0 && i + 1 < result.length) {
        const leftIdx = i - 1
        const rightIdx = i + 1
        const left = parseToken(result[leftIdx])
        const right = parseToken(result[rightIdx])

        // 数字加减计算（8-2 → 6）
        if (left.type === 'num' && right.type === 'num') {
          const sign = op === '+' ? 1 : -1
          const sum = left.num + sign * right.num
          result.splice(leftIdx, 3, String(sum))
          changed = true
          break
        }

        // x 项抵消（-x + x = 0）
        if (left.type === 'x' && right.type === 'x') {
          const sign = op === '+' ? 1 : -1
          const totalCoeff = left.coeff + sign * right.coeff
          if (totalCoeff === 0) {
            result.splice(leftIdx, 3, '0')
          } else if (totalCoeff === 1) {
            result.splice(leftIdx, 3, 'x')
          } else if (totalCoeff === -1) {
            result.splice(leftIdx, 3, '-x')
          } else {
            result.splice(leftIdx, 3, String(totalCoeff) + 'x')
          }
          changed = true
          break
        }
      }
    }

    // 第二趟：处理跨过 x 项的数字抵消（如 6+x-6 → x）
    if (!changed) {
      for (let i = 0; i < result.length; i++) {
        const op = result[i]
        if (op !== '+' && op !== '-') continue

        // 检查是否在括号内
        let depth = 0
        for (let j = 0; j < i; j++) {
          if (result[j] === '(') depth++
          if (result[j] === ')') depth--
        }
        if (depth > 0) continue

        if (i > 0 && i + 1 < result.length) {
          const leftIdx = i - 1
          const rightIdx = i + 1
          const left = parseToken(result[leftIdx])
          const right = parseToken(result[rightIdx])

          // 模式：num + x - num 或 num - x + num
          if (left.type === 'num' && right.type === 'x') {
            // 找到 x 后面的数字和运算符
            let j = rightIdx + 1
            while (j < result.length && (result[j] === '+' || result[j] === '-')) j++
            if (j < result.length) {
              const op2 = j > 0 ? result[j - 1] : '+'
              const nextToken = parseToken(result[j])
              if (nextToken.type === 'num') {
                // 计算：left + op*x + op2*nextToken
                // 只合并数字部分：left + (op * op2) * nextToken
                const sign1 = op === '+' ? 1 : -1
                const sign2 = op2 === '+' ? 1 : -1
                const combinedSign = sign1 * sign2
                const sum = left.num + combinedSign * nextToken.num

                // 替换：移除 left + op + x + op2 + nextToken，保留 x 和计算结果
                // 如果 sum 不为 0，保留 sum；否则只保留 x
                if (sum !== 0) {
                  result.splice(leftIdx, j - leftIdx + 1, String(sum), op, 'x')
                } else {
                  result.splice(leftIdx, j - leftIdx + 1, 'x')
                }
                changed = true
                break
              }
            }
          }
        }
      }
    }
  }

  // 第一趟：移除非开头的 0
  const noZero = []
  for (let i = 0; i < result.length; i++) {
    const t = result[i]
    if (t === '0' && i > 0) continue
    noZero.push(t)
  }

  // 第二趟：清理悬空的运算符（后面没有有效操作数的运算符）
  const filtered = []
  for (let i = 0; i < noZero.length; i++) {
    const t = noZero[i]
    if (t === '+' || t === '-') {
      const next = noZero[i + 1]
      if (!next || next === '+' || next === '-' || next === '*' || next === '/' || next === ')') {
        continue
      }
    }
    filtered.push(t)
  }

  return filtered
}

// 解析一个 token 的类型和值
const parseToken = (t) => {
  if (!isNaN(t)) return { type: 'num', num: parseInt(t) }
  if (t === 'x') return { type: 'x', coeff: 1 }
  if (t === '-x') return { type: 'x', coeff: -1 }
  if (typeof t === 'string' && t.endsWith('x') && !t.includes('/')) {
    const coeff = parseInt(t.replace('x', ''))
    return { type: 'x', coeff: coeff || 1 }
  }
  if (typeof t === 'string' && t.includes('/x')) {
    const num = parseInt(t.replace('/x', ''))
    return { type: 'n/x', num: num || 0 }
  }
  if (typeof t === 'string' && t.startsWith('x/')) {
    const num = parseInt(t.replace('x/', ''))
    return { type: 'x/n', num: num || 0 }
  }
  return { type: 'unknown', value: t }
}

// 简化表达式：处理加减乘除，计算x系数和常数项
const simplify = (tokens) => {
  if (!tokens || tokens.length === 0) {
    return { tokens: [], xCount: 0, constant: 0, hasDivision: false, divisionType: '', divisionValue: 0, display: '0' }
  }

  // 1. 处理括号消失
  let currentTokens = removeOuterParens([...tokens])

  // 2. 处理括号内整体抵消
  currentTokens = processParenCancel(currentTokens)

  // 3. 处理乘除运算（括号作为整体）
  let processed = []
  let i = 0
  while (i < currentTokens.length) {
    const t = currentTokens[i]

    if (t === '(') {
      const endIdx = findMatchingParen(currentTokens, i)
      if (endIdx !== -1) {
        for (let k = i; k <= endIdx; k++) processed.push(currentTokens[k])
        i = endIdx + 1
        continue
      }
    }

    if (t === '*' || t === '/') {
      const prev = processed.pop()
      const next = currentTokens[i + 1]

      if (prev === undefined || next === undefined || next === '*' || next === '/') {
        if (prev !== undefined) processed.push(prev)
        processed.push(t)
        i++
        continue
      }

      // 如果 prev 或 next 是括号，保留原样
      if (prev === '(' || next === '(') {
        processed.push(prev)
        processed.push(t)
        if (next !== '*' && next !== '/') {
          processed.push(next)
          i += 2
        } else {
          i++
        }
        continue
      }

      const left = parseToken(prev)
      const right = parseToken(next)

      if (left.type === 'unknown' || right.type === 'unknown') {
        processed.push(prev)
        processed.push(t)
        i++
        continue
      }

      if (t === '*') {
        if (left.type === 'num' && right.type === 'num') {
          processed.push(String(left.num * right.num))
        } else if ((left.type === 'num' && right.type === 'x') || (left.type === 'x' && right.type === 'num')) {
          const num = left.type === 'num' ? left.num : right.num
          const coeff = left.type === 'x' ? left.coeff : right.coeff
          const c = num * coeff
          if (c === 1) processed.push('x')
          else if (c === -1) processed.push('-x')
          else processed.push(c + 'x')
        } else if (left.type === 'n/x' && right.type === 'x') {
          processed.push(String(left.num))
        } else if (left.type === 'x' && right.type === 'n/x') {
          processed.push(String(right.num))
        } else if (left.type === 'n/x' && right.type === 'num') {
          processed.push((left.num * right.num) + '/x')
        } else if (left.type === 'num' && right.type === 'n/x') {
          processed.push((left.num * right.num) + '/x')
        } else {
          processed.push(prev)
          processed.push(t)
        }
        i += 2
      } else if (t === '/') {
        if (left.type === 'num' && right.type === 'num') {
          if (right.num === 0) {
            processed.push(prev)
            processed.push(t)
          } else {
            const result = left.num / right.num
            if (Number.isInteger(result)) processed.push(String(result))
            else { processed.push(prev); processed.push(t) }
          }
        } else if (left.type === 'x' && right.type === 'num') {
          if (right.num === 0) {
            processed.push(prev)
            processed.push(t)
          } else if (left.coeff % right.num === 0) {
            const c = left.coeff / right.num
            if (c === 1) processed.push('x')
            else if (c === -1) processed.push('-x')
            else processed.push(c + 'x')
          } else {
            processed.push('x/' + right.num)
          }
        } else if (left.type === 'num' && right.type === 'x') {
          processed.push(left.num + '/x')
        } else if (left.type === 'x' && right.type === 'x') {
          if (right.coeff !== 0) {
            const result = left.coeff / right.coeff
            if (Number.isInteger(result)) processed.push(String(result))
            else { processed.push(prev); processed.push(t) }
          } else { processed.push(prev); processed.push(t) }
        } else {
          processed.push(prev)
          processed.push(t)
        }
        i += 2
      }
    } else {
      processed.push(t)
      i++
    }
  }

  // 4. 处理加减运算（括号作为整体）
  let xCount = 0
  let constant = 0
  let hasDivision = false
  let divisionType = ''
  let divisionValue = 0
  let sign = 1

  let j = 0
  while (j < processed.length) {
    const t = processed[j]
    if (t === '+') { sign = 1; j++; continue }
    if (t === '-') { sign = -1; j++; continue }

    if (t === '(') {
      const endIdx = findMatchingParen(processed, j)
      if (endIdx !== -1) {
        const innerTokens = processed.slice(j + 1, endIdx)
        const inner = simplify(innerTokens)
        xCount += sign * inner.xCount
        constant += sign * inner.constant
        sign = 1
        j = endIdx + 1
        continue
      }
    }

    const parsed = parseToken(t)
    if (parsed.type === 'x') {
      xCount += sign * parsed.coeff
    } else if (parsed.type === 'n/x') {
      hasDivision = true
      divisionType = 'n/x'
      divisionValue = sign * parsed.num
    } else if (parsed.type === 'x/n') {
      hasDivision = true
      divisionType = 'x/n'
      divisionValue = sign * parsed.num
    } else if (parsed.type === 'num') {
      constant += sign * parsed.num
    }
    sign = 1
    j++
  }

  // 5. 生成 tokens2
  const tokens2 = []
  if (hasDivision) {
    if (divisionType === 'n/x') tokens2.push(divisionValue + '/x')
    else if (divisionType === 'x/n') tokens2.push('x/' + divisionValue)
    if (constant > 0) tokens2.push('+' + constant)
    else if (constant < 0) tokens2.push(String(constant))
  } else {
    if (xCount > 0) {
      if (xCount === 1) tokens2.push('x')
      else tokens2.push(xCount + 'x')
    } else if (xCount < 0) {
      if (xCount === -1) tokens2.push('-x')
      else tokens2.push(xCount + 'x')
    }
    if (constant > 0) {
      if (tokens2.length > 0) tokens2.push('+' + constant)
      else tokens2.push(String(constant))
    } else if (constant < 0) {
      tokens2.push(String(constant))
    }
  }

  return {
    tokens: tokens2,
    xCount,
    constant,
    hasDivision,
    divisionType,
    divisionValue,
    display: tokens2.length > 0 ? tokens2.join('') : '0'
  }
}

const simplifiedLeft = computed(() => simplify(leftRawTokens.value))
const simplifiedRight = computed(() => simplify(rightRawTokens.value))

// 托盘显示信息：显示原始砝码，当自动简化触发时会更新
const leftRawTokensDisplay = computed(() => {
  return leftRawTokens.value.map((t, idx) => ({
    id: `l-${idx}-${t}-${Date.now()}`,
    display: t,
    coeff: t === 'x' ? 1 : (t === '-x' ? -1 : parseInt(t) || t)
  }))
})

const rightRawTokensDisplay = computed(() => {
  return rightRawTokens.value.map((t, idx) => ({
    id: `r-${idx}-${t}-${Date.now()}`,
    display: t,
    coeff: t === 'x' ? 1 : (t === '-x' ? -1 : parseInt(t) || t)
  }))
})

const leftSimplified = computed(() => simplifiedLeft.value.display)
const rightSimplified = computed(() => simplifiedRight.value.display)
const leftConstant = computed(() => simplifiedLeft.value.constant)
const rightConstant = computed(() => simplifiedRight.value.constant)

// 天平倾斜：基于真实的x值计算
const beamAngle = computed(() => {
  const left = simplifiedLeft.value
  const right = simplifiedRight.value

  // 如果有真实的 x 值，使用真实 x 值计算
  if (solvedXValue.value !== null) {
    const x = solvedXValue.value
    let leftValue, rightValue

    // 计算左边值
    if (left.hasDivision) {
      if (left.divisionType === 'n/x') {
        leftValue = left.divisionValue / x + left.constant
      } else if (left.divisionType === 'x/n') {
        leftValue = x / left.divisionValue + left.constant
      } else {
        leftValue = left.constant
      }
    } else {
      leftValue = left.xCount * x + left.constant
    }

    // 计算右边值
    if (right.hasDivision) {
      if (right.divisionType === 'n/x') {
        rightValue = right.divisionValue / x + right.constant
      } else if (right.divisionType === 'x/n') {
        rightValue = x / right.divisionValue + right.constant
      } else {
        rightValue = right.constant
      }
    } else {
      rightValue = right.xCount * x + right.constant
    }

    const diff = leftValue - rightValue
    const maxAngle = 15
    return -Math.max(-maxAngle, Math.min(maxAngle, diff * 2))
  }

  // 如果没有真实的 x 值（探索模式）
  // 两边都有x项
  if (left.xCount !== 0 && right.xCount !== 0) {
    const xCoeffDiff = left.xCount - right.xCount
    const constDiff = left.constant - right.constant
    if (xCoeffDiff === 0) {
      const diff = constDiff
      const maxAngle = 15
      return -Math.max(-maxAngle, Math.min(maxAngle, diff * 2))
    }
    return 0
  }

  // 一边有x一边没有x
  if (left.xCount !== 0 && right.xCount === 0) {
    return -8
  }
  if (right.xCount !== 0 && left.xCount === 0) {
    return 8
  }

  // 两边都没有x，比较常数项
  const diff = left.constant - right.constant
  const maxAngle = 15
  return -Math.max(-maxAngle, Math.min(maxAngle, diff * 2))
})

const resultText = computed(() => {
  const left = simplifiedLeft.value
  const right = simplifiedRight.value
  
  if (left.tokens.length === 0 && right.tokens.length === 0) return '⚖️ 天平平衡（空）'

  // 如果有真实的 x 值，使用真实 x 值计算
  if (solvedXValue.value !== null) {
    const x = solvedXValue.value
    const leftValue = left.xCount * x + left.constant
    const rightValue = right.xCount * x + right.constant

    if (leftValue === rightValue) {
      return '⚖️ 天平平衡！'
    }
    if (leftValue > rightValue) {
      return '↘️ 左边更重'
    }
    return '↙️ 右边更重'
  }

  // 两边都有x项
  if (left.xCount !== 0 && right.xCount !== 0) {
    if (left.xCount === right.xCount && left.constant === right.constant) {
      return '⚖️ 天平平衡！（两边相同）'
    }
    if (left.xCount > right.xCount) {
      return '↘️ 左边x更多'
    }
    if (right.xCount > left.xCount) {
      return '↙️ 右边x更多'
    }
    return '⚖️ 平衡中（x系数相同时）'
  }

  // 左边有x，右边没有x
  if (left.xCount !== 0 && right.xCount === 0) {
    return '↘️ 左边更重（含有未知数x）'
  }

  // 右边有x，左边没有x
  if (right.xCount !== 0 && left.xCount === 0) {
    return '↙️ 右边更重（含有未知数x）'
  }

  // 两边都没有x，比较常数
  if (left.constant === right.constant) return '⚖️ 天平平衡！'
  if (left.constant > right.constant) return '↘️ 左边更重（常数为 ' + left.constant + '）'
  return '↙️ 右边更重（常数为 ' + right.constant + '）'
})

const resultClass = computed(() => {
  const left = simplifiedLeft.value
  const right = simplifiedRight.value

  if (left.tokens.length === 0 && right.tokens.length === 0) {
    return 'bg-gray-100 text-gray-600 border-2 border-gray-300'
  }

  // 如果有真实的 x 值，使用真实 x 值计算
  if (solvedXValue.value !== null) {
    const x = solvedXValue.value
    let leftValue, rightValue

    // 计算左边值
    if (left.hasDivision) {
      if (left.divisionType === 'n/x') {
        leftValue = left.divisionValue / x + left.constant
      } else if (left.divisionType === 'x/n') {
        leftValue = x / left.divisionValue + left.constant
      } else {
        leftValue = left.constant
      }
    } else {
      leftValue = left.xCount * x + left.constant
    }

    // 计算右边值
    if (right.hasDivision) {
      if (right.divisionType === 'n/x') {
        rightValue = right.divisionValue / x + right.constant
      } else if (right.divisionType === 'x/n') {
        rightValue = x / right.divisionValue + right.constant
      } else {
        rightValue = right.constant
      }
    } else {
      rightValue = right.xCount * x + right.constant
    }

    if (leftValue === rightValue) {
      return 'bg-green-100 text-green-700 border-2 border-green-300'
    }
    if (leftValue > rightValue) {
      return 'bg-blue-100 text-blue-700 border-2 border-blue-300'
    }
    return 'bg-red-100 text-red-700 border-2 border-red-300'
  }

  // 两边都有x项
  if (left.xCount !== 0 && right.xCount !== 0) {
    if (left.xCount === right.xCount && left.constant === right.constant) {
      return 'bg-green-100 text-green-700 border-2 border-green-300'
    }
    if (left.xCount > right.xCount) {
      return 'bg-blue-100 text-blue-700 border-2 border-blue-300'
    }
    if (right.xCount > left.xCount) {
      return 'bg-red-100 text-red-700 border-2 border-red-300'
    }
    return 'bg-purple-100 text-purple-700 border-2 border-purple-300'
  }

  // 一边有x一边没有x
  if (left.xCount !== 0 && right.xCount === 0) {
    return 'bg-blue-100 text-blue-700 border-2 border-blue-300'
  }
  if (right.xCount !== 0 && left.xCount === 0) {
    return 'bg-red-100 text-red-700 border-2 border-red-300'
  }

  // 两边都没有x，比较常数
  if (left.constant === right.constant) {
    return 'bg-green-100 text-green-700 border-2 border-green-300'
  }
  if (left.constant > right.constant) {
    return 'bg-blue-100 text-blue-700 border-2 border-blue-300'
  }
  return 'bg-red-100 text-red-700 border-2 border-red-300'
})

const solvedX = computed(() => {
  const left = simplifiedLeft.value
  const right = simplifiedRight.value
  
  if (left.xCount === 1 && right.xCount === 0 && left.constant === right.constant) {
    return right.constant
  }
  if (right.xCount === 1 && left.xCount === 0 && left.constant === right.constant) {
    return left.constant
  }
  return null
})

const stepHint = computed(() => {
  const left = simplifiedLeft.value
  const right = simplifiedRight.value
  
  if (left.tokens.length === 0 && right.tokens.length === 0) return ''
  
  // 两边都有x
  if (left.xCount !== 0 && right.xCount !== 0) {
    if (left.xCount === right.xCount && left.constant === right.constant) {
      return '两边完全相同，天平平衡！'
    }
    return '两边都有 x 项，无法直接比较，继续操作使等式成立'
  }
  
  // 一边有x一边没有
  if (left.xCount === 1 && right.xCount === 0) {
    if (right.constant !== 0) {
      return '左边只剩 x，右边是数字 ' + right.constant + '，所以 x = ' + right.constant + '！'
    }
    return '左边只剩 x，右边为空，x = ?'
  }
  if (right.xCount === 1 && left.xCount === 0) {
    if (left.constant !== 0) {
      return '右边只剩 x，左边是数字 ' + left.constant + '，所以 x = ' + left.constant + '！'
    }
    return '右边只剩 x，左边为空，x = ?'
  }
  
  // 两边都没有x
  if (left.constant > right.constant) {
    return '左边常数 ' + left.constant + ' > 右边常数 ' + right.constant + '，需要消减左边的数或增加右边的数'
  }
  if (left.constant < right.constant) {
    return '右边常数 ' + right.constant + ' > 左边常数 ' + left.constant + '，需要消减右边的数或增加左边的数'
  }
  
  return ''
})

// 判断表达式是否完整（没有悬空的运算符）
const isExpressionComplete = (tokens) => {
  if (tokens.length === 0) return true
  const last = tokens[tokens.length - 1]
  // 最后一个不能是运算符
  if (last === '+' || last === '-' || last === '*' || last === '/') return false
  return true
}

// 将 simplify 的结果转换为 tokens 数组（用于自动简化）
const simplifyResultToTokens = (simplified) => {
  if (simplified.tokens.length === 0) return []
  const result = []
  for (const t of simplified.tokens) {
    if (t === 'x' || t === '-x') {
      result.push(t)
    } else if (typeof t === 'string') {
      // 处理 x/n 格式 -> ['x', '/', n]
      if (t.startsWith('x/') && t.length > 2) {
        result.push('x', '/', t.replace('x/', ''))
      }
      // 处理 n/x 格式 -> [n, '/', 'x']
      else if (t.includes('/x') && !t.startsWith('x/')) {
        result.push(t.replace('/x', ''), '/', 'x')
      }
      // 处理 nx 格式（如 7x, -7x）
      else if (t.endsWith('x') && t.length > 1) {
        result.push(t)
      }
      // 处理普通数字
      else {
        const num = parseInt(t)
        if (!isNaN(num)) {
          result.push(String(num))
        } else {
          result.push(t)
        }
      }
    }
  }
  return result
}

// watch tokens 变化：处理 challenge 模式 + 括号消失
let isAutoSimplifying = false  // 防止递归触发
watch([leftRawTokens, rightRawTokens], () => {
  if (isAutoSimplifying) return
  isAutoSimplifying = true

  if (mode.value === 'challenge') {
    if (solvedX.value !== null) {
      showXResult.value = true
    } else {
      showXResult.value = false
    }
  }

  // 处理括号相关逻辑：整体抵消、加减抵消、括号消失
  if (isExpressionComplete(leftRawTokens.value)) {
    let simplified = processParenCancel([...leftRawTokens.value])
    simplified = processAddSubCancel(simplified)
    simplified = removeOuterParens(simplified)
    if (JSON.stringify(simplified) !== JSON.stringify(leftRawTokens.value)) {
      leftRawTokens.value = simplified
    }
  }

  if (isExpressionComplete(rightRawTokens.value)) {
    let simplified = processParenCancel([...rightRawTokens.value])
    simplified = processAddSubCancel(simplified)
    simplified = removeOuterParens(simplified)
    if (JSON.stringify(simplified) !== JSON.stringify(rightRawTokens.value)) {
      rightRawTokens.value = simplified
    }
  }

  setTimeout(() => {
    isAutoSimplifying = false
  }, 0)
}, { deep: true })

const setChallengeMode = () => {
  mode.value = 'challenge'
  studentAnswer.value = null
  answerFeedback.value = ''
  showXResult.value = false

  const challenges = [
    { left: 'x + 3', right: '8' },
    { left: 'x + 5', right: '12' },
    { left: 'x - 2', right: '7' },
    { left: '3 - x', right: '2' },
    { left: '(x + 3) + 2', right: '7' },
    { left: '2 * (x - 1)', right: '8' },
    { left: '(2 + 3) * x', right: '25' },
    { left: '(x + 2) * 3', right: '15' },
  ]

  const challenge = challenges[Math.floor(Math.random() * challenges.length)]

  // 根据目标方程设置初始状态
  leftRawTokens.value = parseExpression(challenge.left)
  rightRawTokens.value = parseExpression(challenge.right)

  challengeEquation.value = challenge
}

const checkAnswer = () => {
  if (studentAnswer.value === null) return
  
  const expected = solvedX.value
  if (expected !== null && studentAnswer.value === expected) {
    answerFeedback.value = '正确！'
  } else if (expected !== null) {
    answerFeedback.value = `不对哦，x = ${expected}`
  } else {
    answerFeedback.value = '还没有求出 x 的值'
  }
}

const getChipClass = (token) => {
  let value = token
  if (typeof token === 'object' && token !== null && token.display !== undefined) {
    value = token.display
  }

  if (value === 'x' || value === '-x') {
    return 'bg-purple-200 text-purple-900 border-purple-400 cursor-grab'
  }
  if (['+', '-', '*', '/'].includes(value)) {
    return 'bg-blue-200 text-blue-900 border-blue-400 cursor-grab'
  }
  if (value === '(' || value === ')') {
    return 'bg-gray-300 text-gray-700 border-gray-500 cursor-default px-2'
  }
  if (typeof value === 'string') {
    if (value.startsWith('-')) {
      if (value === '-x') return 'bg-purple-200 text-purple-900 border-purple-400 cursor-grab'
      return 'bg-red-100 text-red-800 border-red-300 cursor-grab'
    }
    if (value.startsWith('+')) {
      if (value === '+x') return 'bg-purple-200 text-purple-900 border-purple-400 cursor-grab'
      return 'bg-green-100 text-green-800 border-green-300 cursor-grab'
    }
    if (value.startsWith('*')) {
      return 'bg-blue-100 text-blue-800 border-blue-300 cursor-grab'
    }
    if (value.startsWith('/')) {
      return 'bg-orange-100 text-orange-800 border-orange-300 cursor-grab'
    }
  }
  if (typeof value === 'number' && value < 0) {
    return 'bg-red-100 text-red-800 border-red-300 cursor-grab'
  }
  return 'bg-green-100 text-green-800 border-green-300 cursor-grab'
}

const getGroupClass = (color) => {
  const classes = {
    green: 'bg-green-50 border-green-200',
    red: 'bg-red-50 border-red-200',
    blue: 'bg-blue-50 border-blue-200',
    orange: 'bg-orange-50 border-orange-200'
  }
  return classes[color] || 'bg-gray-50 border-gray-200'
}

const getGroupTitleClass = (color) => {
  const classes = {
    green: 'text-green-700',
    red: 'text-red-700',
    blue: 'text-blue-700',
    orange: 'text-orange-700'
  }
  return classes[color] || 'text-gray-700'
}

const getGroupBadgeBg = (color) => {
  const classes = {
    green: 'bg-green-100',
    red: 'bg-red-100',
    blue: 'bg-blue-100',
    orange: 'bg-orange-100'
  }
  return classes[color] || 'bg-gray-100'
}

const removeFromTray = (side, idx) => {
  if (side === 'left') {
    leftRawTokens.value = leftRawTokens.value.filter((_, i) => i !== idx)
  } else {
    rightRawTokens.value = rightRawTokens.value.filter((_, i) => i !== idx)
  }
}

const resetAll = () => {
  leftRawTokens.value = []
  rightRawTokens.value = []
  showXResult.value = false
  answerFeedback.value = ''
  studentAnswer.value = null
  challengeEquation.value = null
  mode.value = 'explore'
  inputEquation.value = ''
  equationError.value = ''
  solvedXValue.value = null
}

const parseExpression = (expr) => {
  const tokens = []
  expr = expr.replace(/\s+/g, '')
  
  let i = 0
  while (i < expr.length) {
    const char = expr[i]
    
    // x 变量
    if (char === 'x') {
      tokens.push('x')
      i++
    }
    // 操作符 + - * /
    else if (['+', '*', '/'].includes(char)) {
      tokens.push(char)
      i++
    }
    // 负号（需要判断是一元负号还是二元减号）
    else if (char === '-') {
      // 判断是否是一元负号：位于开头、或前一个token是左括号/操作符/=
      const prevToken = tokens[tokens.length - 1]
      const isUnaryMinus = tokens.length === 0 || 
                           prevToken === '(' || 
                           prevToken === '+' || 
                           prevToken === '-' || 
                           prevToken === '*' || 
                           prevToken === '/' ||
                           prevToken === '='
      
      if (i + 1 < expr.length) {
        const nextChar = expr[i + 1]
        if (nextChar === 'x') {
          // -x
          tokens.push('-x')
          i += 2
        } else if (/\d/.test(nextChar)) {
          // 负数如 -3
          let num = '-'
          i++ // 跳过负号
          while (i < expr.length && /\d/.test(expr[i])) {
            num += expr[i]
            i++
          }
          tokens.push(num)
        } else {
          // 二元减号
          tokens.push('-')
          i++
        }
      } else {
        // 末尾的负号当作二元减号
        tokens.push('-')
        i++
      }
    }
    // 数字
    else if (/\d/.test(char)) {
      let num = ''
      while (i < expr.length && /\d/.test(expr[i])) {
        num += expr[i]
        i++
      }
      tokens.push(num)
    }
    // 左括号
    else if (char === '(') {
      tokens.push('(')
      i++
    }
    // 右括号
    else if (char === ')') {
      tokens.push(')')
      i++
    }
    else {
      i++
    }
  }
  
  return tokens
}

const parseEquation = () => {
  const eq = inputEquation.value.trim()
  if (!eq) {
    equationError.value = '请输入方程'
    return
  }

  const parts = eq.split('=')
  if (parts.length !== 2) {
    equationError.value = '方程格式错误，请使用 = 分隔左右两边'
    return
  }

  const leftExpr = parts[0].trim()
  const rightExpr = parts[1].trim()

  const leftTokens = parseExpression(leftExpr)
  const rightTokens = parseExpression(rightExpr)

  if (leftTokens.length === 0 && rightTokens.length === 0) {
    equationError.value = '方程不能为空'
    return
  }

  leftRawTokens.value = leftTokens
  rightRawTokens.value = rightTokens
  equationError.value = ''
  mode.value = 'explore'

  // 计算真实的 x 值（不显示）
  const left = simplify(leftTokens)
  const right = simplify(rightTokens)

  // 处理含除法的方程
  if (left.hasDivision || right.hasDivision) {
    // 左边有除法，如 8/x = 4
    if (left.hasDivision && !right.hasDivision) {
      if (left.divisionType === 'n/x') {
        // n/x = right => x = n/right
        solvedXValue.value = left.divisionValue / right.constant
      } else if (left.divisionType === 'x/n') {
        // x/n = right => x = right * n
        solvedXValue.value = right.constant * left.divisionValue
      }
    }
    // 右边有除法，如 4 = 8/x
    else if (right.hasDivision && !left.hasDivision) {
      if (right.divisionType === 'n/x') {
        // left = n/x => x = n/left
        solvedXValue.value = right.divisionValue / left.constant
      } else if (right.divisionType === 'x/n') {
        // left = x/n => x = left * n
        solvedXValue.value = left.constant * right.divisionValue
      }
    }
    // 两边都有除法
    else {
      solvedXValue.value = null
    }
  } else {
    // 普通加减方程
    // 方程: left.xCount * x + left.constant = right.xCount * x + right.constant
    // 移项: (left.xCount - right.xCount) * x = right.constant - left.constant
    const xCoeff = left.xCount - right.xCount
    const constDiff = right.constant - left.constant

    if (xCoeff === 0) {
      solvedXValue.value = null
    } else {
      solvedXValue.value = constDiff / xCoeff
    }
  }
}

</script>

<style scoped>
.weight-chip {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px 8px;
  border: 2px solid;
  border-radius: 8px;
  user-select: none;
  transition: all 0.2s ease;
  min-height: 38px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  font-size: 14px;
}

.weight-chip:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.beam-rotate {
  transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.result-badge {
  transition: all 0.3s ease;
}

.drop-zone {
  transition: all 0.2s ease;
}

.token-enter-active,
.token-leave-active {
  transition: all 0.5s ease;
}

.token-enter-from,
.token-leave-to {
  opacity: 0;
  transform: scale(0.5);
}

.token-move {
  transition: transform 0.3s ease;
}
</style>
