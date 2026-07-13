<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex gap-4">
      <div class="flex-1">
        <div class="border border-gray-300">
          <svg v-if="!showCube" class="w-full" viewBox="0 0 800 500">
            <defs>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e5e7eb" stroke-width="0.5"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)"/>
            
            <g v-if="currentStep === 1">
              <line x1="50" :y1="planeBottomY" x2="750" :y2="planeBottomY" stroke="#d1d5db" stroke-width="2" stroke-dasharray="5,5"/>
              <circle :cx="basePosition" :cy="planeBottomY" r="12" fill="#ef4444" stroke="white" stroke-width="3"/>
              <circle :cx="endPosition" :cy="planeBottomY" r="12" fill="#22c55e" stroke="white" stroke-width="3"/>
              <line :x1="basePosition" :y1="planeBottomY"
                    :x2="basePosition + lineAnimProgress * (endPosition - basePosition)"
                    :y2="planeBottomY"
                    stroke="#3b82f6" stroke-width="4" stroke-linecap="round"/>
              <text :x="basePosition" :y="planeBottomY + 25" text-anchor="middle" class="text-xs" fill="#6b7280">起点</text>
              <text :x="endPosition" :y="planeBottomY + 25" text-anchor="middle" class="text-xs" fill="#6b7280">终点</text>
              <text :x="(basePosition + endPosition)/2" :y="planeBottomY - 25" text-anchor="middle" class="text-base font-bold" fill="#8b5cf6">向前移动{{ bLength }}</text>
              <text x="400" :y="planeBottomY - 60" text-anchor="middle" class="text-base font-bold" fill="#8b5cf6">长度 = 起点({{ aLength }}) + 向前移动多少({{ bLength }}) = {{ lineLength }}</text>
            </g>
            
            <g v-if="currentStep >= 2">
              <line x1="50" :y1="planeBottomY - displayHeight - 20" x2="750" :y2="planeBottomY - displayHeight - 20" stroke="#d1d5db" stroke-width="2" stroke-dasharray="5 5"/>
              <line x1="50" :y1="planeBottomY + 10" x2="750" :y2="planeBottomY + 10" stroke="#d1d5db" stroke-width="2" stroke-dasharray="5 5"/>
              <g v-for="i in planeAnimLines" :key="i">
                <rect :x="basePosition" :y="planeBottomY - i*lineSpacing"
                      :width="endPosition - basePosition" :height="lineSpacing"
                      fill="#3b82f6"/>
                <circle :cx="basePosition" :cy="planeBottomY - (i-0.5)*lineSpacing" r="10" fill="#ef4444" stroke="white" stroke-width="2"/>
                <circle :cx="endPosition" :cy="planeBottomY - (i-0.5)*lineSpacing" r="10" fill="#22c55e" stroke="white" stroke-width="2"/>
              </g>
              <g v-if="planeAnimProgress >= 1">
                <polygon :points="rectanglePoints" fill="rgba(209,250,229,0.3)" stroke="#22c55e" stroke-width="3"/>
                <text x="400" :y="planeBottomY - displayHeight - 35" text-anchor="middle" class="text-xs font-bold" fill="#6b7280">
                  周长: {{ lineLength }}+{{ additionalLines + 1 }}+{{ lineLength }}+{{ additionalLines + 1 }} = 2×{{ lineLength }}+2×{{ additionalLines + 1 }} = 2×({{ lineLength }}+{{ additionalLines + 1 }}) = {{ perimeter }}
                </text>
                <text x="400" :y="planeBottomY + 35" text-anchor="middle" class="text-base font-bold" fill="#6b7280">
                  面积: {{ lineLength }}×{{ additionalLines + 1 }} = {{ area }}
                </text>
              </g>
            </g>
          </svg>
          
          <div v-if="showCube" ref="threeContainer" class="w-full h-[500px]"></div>
          
          <div class="mt-4">
            <button @click="resetAll" 
              class="w-full px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm">
              🔄 重置
            </button>
          </div>
        </div>
      </div>
      
      <div class="w-96 bg-gray-50 p-4">
        <h3 class="font-bold text-lg mb-4">几何建模流程</h3>
        
        <div class="space-y-4 text-sm">
          <div class="flex gap-2 mb-4">
            <div v-for="i in 3" :key="i" :class="stepClass(i)">
              {{ i === 1 ? '1.线段' : i === 2 ? '2.平面' : '3.立方体' }}
            </div>
          </div>
          
          <div class="bg-blue-50 p-3 rounded-lg border-l-4 border-blue-500">
            <div class="font-medium text-blue-800 mb-2">步骤 1: 定义线段</div>
            <div class="space-y-2">
              <div>
                <label class="text-xs text-gray-600">起点:</label>
                <input v-model.number="aLength" type="number" placeholder="例如: 100" class="w-full px-2 py-1 border rounded text-sm"/>
              </div>
              <div>
                <label class="text-xs text-gray-600">向前移动多少:</label>
                <input v-model.number="bLength" type="number" placeholder="例如: 150" class="w-full px-2 py-1 border rounded text-sm"/>
              </div>
            </div>
            <div class="mt-2 text-xs text-gray-600">
              长度 = 起点(<span class="font-bold text-red-500">{{ aLength }}</span>) + 移动数(<span class="font-bold text-green-600">{{ bLength }}</span>) = <span class="font-bold text-blue-600">{{ lineLength }}</span>
            </div>
            <button @click="drawLine" :disabled="currentStep < 1" 
              class="mt-2 w-full px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm">
              绘制线段
            </button>
          </div>
          
          <div class="bg-purple-50 p-3 rounded-lg border-l-4 border-purple-500" :class="currentStep < 2 ? 'opacity-50' : ''">
            <div class="font-medium text-purple-800 mb-2">步骤 2: 线段平铺成平面</div>
            <div>
              <label class="text-xs text-gray-600">增加多少条同样的线段:</label>
              <input v-model.number="additionalLines" type="number" placeholder="例如: 3" class="w-full px-2 py-1 border rounded text-sm"/>
            </div>
            <div class="mt-2 text-xs text-gray-600 space-y-1">
              <div>长: <span class="font-bold text-purple-600">{{ lineLength }}</span></div>
              <div>线条的数量: <span class="font-bold text-purple-600">{{ additionalLines + 1 }}</span></div>
              <div>周长: <span class="font-bold text-purple-600">{{ lineLength }}+{{ additionalLines + 1 }}+{{ lineLength }}+{{ additionalLines + 1 }} = 2×{{ lineLength }}+2×{{ additionalLines + 1 }} = 2×({{ lineLength }}+{{ additionalLines + 1 }}) = {{ perimeter }}</span></div>
              <div>面积: <span class="font-bold text-purple-600">{{ lineLength }}×{{ additionalLines + 1 }} = {{ area }}</span></div>
            </div>
            <button @click="drawPlane" :disabled="currentStep < 2" 
              class="mt-2 w-full px-3 py-1 bg-purple-500 text-white rounded hover:bg-purple-600 text-sm">
              生成平面
            </button>
          </div>
          
          <div class="bg-orange-50 p-3 rounded-lg border-l-4 border-orange-500" :class="currentStep < 3 ? 'opacity-50' : ''">
            <div class="font-medium text-orange-800 mb-2">步骤 3: 创建立方体</div>
            <div>
              <label class="text-xs text-gray-600">高（平面重叠数量）:</label>
              <input v-model.number="cubeHeightCount" type="number" placeholder="例如: 5" class="w-full px-2 py-1 border rounded text-sm"/>
            </div>
            <div class="mt-2 text-xs text-gray-600 space-y-1">
              <div>长: <span class="font-bold text-orange-600">{{ lineLength }}</span></div>
              <div>宽: <span class="font-bold text-orange-600">{{ additionalLines + 1 }}</span></div>
              <div>高: <span class="font-bold text-orange-600">{{ cubeHeightCount }}</span></div>
              <div>体积: <span class="font-bold text-orange-600">{{ lineLength }}×{{ additionalLines + 1 }}×{{ cubeHeightCount }} = {{ cubeVolume }}</span></div>
              <div>棱长: <span class="font-bold text-orange-600">({{ lineLength }}+{{ additionalLines + 1 }}+{{ cubeHeightCount }})×4 = {{ lineLength + (additionalLines + 1) + cubeHeightCount }}×4 = {{ cubeEdgeLength }}</span></div>
              <div>表面积: <span class="font-bold text-orange-600">2×({{ lineLength }}×{{ additionalLines + 1 }}+{{ lineLength }}×{{ cubeHeightCount }}+{{ additionalLines + 1 }}×{{ cubeHeightCount }}) = {{ cubeSurfaceArea }}</span></div>
            </div>
            <button @click="drawCube" :disabled="currentStep < 3" 
              class="mt-2 w-full px-3 py-1 bg-orange-500 text-white rounded hover:bg-orange-600 text-sm">
              创建立方体
            </button>
          </div>
          
          <div class="mt-4 flex gap-2">
            <button @click="prevStep" :disabled="currentStep <= 1" 
              class="flex-1 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm">
              上一步
            </button>
            <button @click="resetAll" 
              class="flex-1 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm">
              重置
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onUnmounted } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

const aLength = ref(100)
const bLength = ref(150)
const additionalLines = ref(3)
const cubeHeightCount = ref(5)
const currentStep = ref(1)
const lineAnimProgress = ref(0)
const planeAnimProgress = ref(0)
const showCube = ref(false)

const canvasWidth = 800
const canvasHeight = 500

const marginLeft = 80
const marginRight = 80
const marginBottom = 100
const marginTop = 80
const availableWidth = canvasWidth - marginLeft - marginRight
const availableHeight = canvasHeight - marginBottom - marginTop

const scaleFactor = computed(() => {
  const requiredWidth = aLength.value + bLength.value
  const requiredHeight = (additionalLines.value + 1) * 20
  const widthScale = availableWidth / requiredWidth
  const heightScale = availableHeight / requiredHeight
  return Math.min(1, widthScale, heightScale)
})

const displayWidth = computed(() => (aLength.value + bLength.value) * scaleFactor.value)
const displayHeight = computed(() => (additionalLines.value + 1) * 20 * scaleFactor.value)

const basePosition = computed(() => (canvasWidth - displayWidth.value) / 2)
const endPosition = computed(() => basePosition.value + displayWidth.value)

const planeBottomY = computed(() => canvasHeight - marginBottom - 30)

const lineSpacing = computed(() => 20 * scaleFactor.value)

const lineLength = computed(() => aLength.value + bLength.value)

const planeWidth = computed(() => displayHeight.value)
const planeAnimLines = computed(() => {
  const totalLines = additionalLines.value + 1
  const visibleLines = Math.max(1, Math.min(totalLines, Math.ceil(planeAnimProgress.value * totalLines)))
  return Array.from({ length: visibleLines }, (_, i) => i + 1)
})

const perimeter = computed(() => 2 * (lineLength.value + additionalLines.value + 1))
const area = computed(() => lineLength.value * (additionalLines.value + 1))

const rectanglePoints = computed(() => {
  const minX = basePosition.value
  const maxX = endPosition.value
  const minY = planeBottomY.value - displayHeight.value
  const maxY = planeBottomY.value
  return `${minX},${minY} ${maxX},${minY} ${maxX},${maxY} ${minX},${maxY}`
})

const cubeVolume = computed(() => lineLength.value * (additionalLines.value + 1) * cubeHeightCount.value)
const cubeEdgeLength = computed(() => (lineLength.value + additionalLines.value + 1 + cubeHeightCount.value) * 4)
const cubeSurfaceArea = computed(() => {
  const w = lineLength.value
  const h = additionalLines.value + 1
  const f = cubeHeightCount.value
  return 2 * (w*h + w*f + h*f)
})

const threeContainer = ref(null)
let scene, camera, renderer, cubeGroup, controls, animationId, cubeAnimProgress = 0
let targetWidth, targetHeight, targetDepth, totalLayers

const stepClass = (i) => {
  const base = 'flex-1 py-2 text-center rounded text-xs font-medium transition-all'
  if (currentStep.value === i) {
    return `${base} bg-blue-500 text-white`
  } else if (currentStep.value > i) {
    return `${base} bg-green-500 text-white`
  } else {
    return `${base} bg-gray-200 text-gray-600`
  }
}

const drawLine = () => {
  currentStep.value = 2
  lineAnimProgress.value = 0
  let progress = 0
  const animate = () => {
    progress += 0.01
    lineAnimProgress.value = Math.min(progress, 1)
    if (progress < 1) requestAnimationFrame(animate)
  }
  animate()
}

const drawPlane = () => {
  planeAnimProgress.value = 0
  let progress = 0
  const animate = () => {
    progress += 0.008
    planeAnimProgress.value = Math.min(progress, 1.2)
    if (progress < 1.2) {
      requestAnimationFrame(animate)
    } else {
      currentStep.value = 3
    }
  }
  animate()
}

const drawCube = async () => {
  showCube.value = true
  currentStep.value = 3
  await nextTick()
  initThree()
  createCube()
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
    if (currentStep.value < 3) showCube.value = false
  }
}

const resetAll = () => {
  currentStep.value = 1
  lineAnimProgress.value = 0
  planeAnimProgress.value = 0
  showCube.value = false
}

const initThree = () => {
  if (!threeContainer.value) return
  
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xf5f5f5)
  
  const width = threeContainer.value.clientWidth
  const height = 500
  
  camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000)
  camera.position.set(4, 3, 4)
  camera.lookAt(0, 0, 0)
  
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(window.devicePixelRatio)
  threeContainer.value.innerHTML = ''
  threeContainer.value.appendChild(renderer.domElement)
  
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.minDistance = 2
  controls.maxDistance = 20
  
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambientLight)
  
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(5, 5, 5)
  scene.add(directionalLight)
}

const createCube = () => {
  if (cubeGroup) scene.remove(cubeGroup)
  
  cubeGroup = new THREE.Group()
  scene.add(cubeGroup)
  
  // 统一的缩放因子，确保立方体在视野范围内
  const maxSize = 4
  const requiredWidth = lineLength.value / 100
  const requiredHeight = cubeHeightCount.value  // 高度 = 面的数量
  const requiredDepth = additionalLines.value + 1  // 深度 = 线条数量
  
  // 找出最大的维度，计算统一的缩放比例
  const maxDimension = Math.max(requiredWidth, requiredHeight, requiredDepth)
  const cubeScale = maxSize / maxDimension
  
  targetWidth = requiredWidth * cubeScale
  targetHeight = requiredHeight * cubeScale
  targetDepth = requiredDepth * cubeScale
  totalLayers = cubeHeightCount.value
  
  // 根据立方体大小调整相机位置
  if (camera) {
    const maxExtent = Math.max(targetWidth, targetHeight, targetDepth)
    const distance = Math.max(6, maxExtent * 2.5)
    camera.position.set(distance, distance * 0.75, distance)
    camera.lookAt(0, 0, 0)
  }
  
  // 每个面的高度为1（逻辑单位，缩放后相应缩放）
  const faceHeight = targetHeight / totalLayers
  const faceSpacing = faceHeight  // 面之间的间距等于面高度
  
  for (let i = 0; i < totalLayers; i++) {
    // 每个面使用独立材质，便于单独控制透明度
    const material = new THREE.MeshPhongMaterial({ 
      color: 0x8b5cf6, 
      shininess: 100, 
      transparent: true, 
      opacity: 0,
      side: THREE.DoubleSide
    })
    
    // 每个面是一个完整的面：宽 x 高度(1) x 深
    const geometry = new THREE.BoxGeometry(targetWidth, faceHeight, targetDepth)
    const face = new THREE.Mesh(geometry, material)
    // 目标位置（从下往上排列，i=0是最底部）
    const targetY = -targetHeight / 2 + (i + 0.5) * faceHeight
    // 初始位置（在最上面，透明不可见）
    face.position.y = targetHeight / 2 + faceHeight
    face.userData.targetY = targetY
    cubeGroup.add(face)
  }
  
  cubeAnimProgress = 0
  animate3D()
}

const animateCubeScale = () => {
  if (!cubeGroup || cubeAnimProgress >= 1) return false
  
  cubeAnimProgress += 0.008
  
  // 每个面需要的动画进度
  const progressPerFace = 1 / totalLayers
  
  for (let i = 0; i < totalLayers; i++) {
    const face = cubeGroup.children[i]
    if (!face) continue
    
    const targetY = face.userData.targetY
    const faceStartProgress = i * progressPerFace
    const faceEndProgress = (i + 1) * progressPerFace
    const startY = targetHeight / 2 + targetHeight / totalLayers
    
    if (cubeAnimProgress < faceStartProgress) {
      // 这个面还没轮到，保持在顶部，透明
      face.position.y = startY
      face.material.opacity = 0
    } else if (cubeAnimProgress < faceEndProgress) {
      // 这个面正在动画：前半段下落（透明），后半段渐变为不透明
      const faceProgress = (cubeAnimProgress - faceStartProgress) / progressPerFace
      
      if (faceProgress < 0.6) {
        // 前60%时间：从顶部下落到目标位置，保持透明
        const fallProgress = faceProgress / 0.6
        const easedFall = 1 - Math.pow(1 - fallProgress, 3)
        face.position.y = startY + (targetY - startY) * easedFall
        face.material.opacity = 0
      } else {
        // 后40%时间：保持在目标位置，从不透明渐变到不透明
        const fadeProgress = (faceProgress - 0.6) / 0.4
        const easedFade = 1 - Math.pow(1 - fadeProgress, 2)
        face.position.y = targetY
        face.material.opacity = easedFade * 0.85
      }
    } else {
      // 这个面已经完成，保持在目标位置，完全可见
      face.position.y = targetY
      face.material.opacity = 0.85
    }
  }
  
  return cubeAnimProgress < 1
}

const animate3D = () => {
  if (!renderer) return
  animationId = requestAnimationFrame(animate3D)
  
  animateCubeScale()
  
  if (controls) {
    controls.update()
  }
  
  renderer.render(scene, camera)
}

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (renderer) renderer.dispose()
})
</script>
