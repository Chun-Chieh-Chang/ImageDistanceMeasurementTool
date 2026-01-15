const state={mode:"line",scaleValue:0,unit:"mm",imgA:null,imgB:null,pointsA:[],pointsB:[],zoomA:1.0,zoomB:1.0}
const el={
  modeInputs:()=>document.querySelectorAll('input[name="mode"]'),
  actualDist:()=>document.getElementById('actualDist'),
  unitSel:()=>document.getElementById('unitSel'),
  setScaleBtn:()=>document.getElementById('setScaleBtn'),
  scaleDisplay:()=>document.getElementById('scaleDisplay'),
  resetBtn:()=>document.getElementById('resetBtn'),
  clearA:()=>document.getElementById('clearA'),
  clearB:()=>document.getElementById('clearB'),
  fileA:()=>document.getElementById('fileA'),
  fileB:()=>document.getElementById('fileB'),
  canvasA:()=>document.getElementById('canvasA'),
  canvasB:()=>document.getElementById('canvasB'),
  wrapA:()=>document.getElementById('wrapA'),
  wrapB:()=>document.getElementById('wrapB'),
  pointsA:()=>document.getElementById('pointsA'),
  pointsB:()=>document.getElementById('pointsB'),
  distX:()=>document.getElementById('distX'),
  distY:()=>document.getElementById('distY'),
  coordA:()=>document.getElementById('coordA'),
  logBox:()=>document.getElementById('logBox'),
  zoomInA:()=>document.getElementById('zoomInA'),
  zoomOutA:()=>document.getElementById('zoomOutA'),
  zoomResetA:()=>document.getElementById('zoomResetA'),
  zoomLabelA:()=>document.getElementById('zoomLabelA'),
  zoomInB:()=>document.getElementById('zoomInB'),
  zoomOutB:()=>document.getElementById('zoomOutB'),
  zoomResetB:()=>document.getElementById('zoomResetB'),
  zoomLabelB:()=>document.getElementById('zoomLabelB'),
}
function log(msg){
  const t=el.logBox()
  t.value+=msg+"\n"
  t.scrollTop=t.scrollHeight
}
function setCanvasImage(canvas,img,zoom){
  const ctx=canvas.getContext('2d')
  const w=Math.max(1,Math.floor(img.width*zoom))
  const h=Math.max(1,Math.floor(img.height*zoom))
  canvas.width=w
  canvas.height=h
  ctx.clearRect(0,0,w,h)
  ctx.drawImage(img,0,0,w,h)
  return {w,h,ratio:zoom}
}
let dispA=null,dispB=null
function redrawA(){
  const c=el.canvasA()
  if(!state.imgA)return
  dispA=setCanvasImage(c,state.imgA,state.zoomA)
  drawPointsAndShapes(c,state.pointsA,dispA,true)
  el.zoomLabelA().textContent=`縮放: ${Math.round(state.zoomA*100)}% | Zoom: ${Math.round(state.zoomA*100)}%`
}
function redrawB(){
  const c=el.canvasB()
  if(!state.imgB)return
  dispB=setCanvasImage(c,state.imgB,state.zoomB)
  drawPointsAndShapes(c,state.pointsB,dispB,false)
  el.zoomLabelB().textContent=`縮放: ${Math.round(state.zoomB*100)}% | Zoom: ${Math.round(state.zoomB*100)}%`
}
function imgToCanvasCoord(origX,origY,disp){
  return {x:origX*disp.ratio,y:origY*disp.ratio}
}
function canvasToImgCoord(x,y,disp){
  return {x:x/disp.ratio,y:y/disp.ratio}
}
function drawPointsAndShapes(canvas,points,disp,isA){
  const ctx=canvas.getContext('2d')
  ctx.clearRect(0,0,canvas.width,canvas.height)
  if(isA&&state.imgA)ctx.drawImage(state.imgA,0,0,disp.w,disp.h)
  if(!isA&&state.imgB)ctx.drawImage(state.imgB,0,0,disp.w,disp.h)
  for(let i=0;i<points.length;i++){
    const p=imgToCanvasCoord(points[i].x,points[i].y,disp)
    ctx.beginPath()
    ctx.arc(p.x,p.y,4,0,Math.PI*2)
    ctx.fillStyle=isA?"red":"blue"
    ctx.strokeStyle="#fff"
    ctx.lineWidth=1
    ctx.fill()
    ctx.stroke()
  }
  if(points.length===2){
    const p1=imgToCanvasCoord(points[0].x,points[0].y,disp)
    const p2=imgToCanvasCoord(points[1].x,points[1].y,disp)
  ctx.lineWidth=2
  ctx.strokeStyle=isA?"red":"blue"
  const dxImg=points[1].x-points[0].x
  const dyImg=points[1].y-points[0].y
  const pixD=Math.hypot(dxImg,dyImg)
  let text=""
  if(!isA){
    text=`像素: ${pixD.toFixed(1)} px`
    ctx.beginPath()
    ctx.moveTo(p1.x,p1.y);ctx.lineTo(p2.x,p2.y);ctx.stroke()
    drawText(ctx,text,(p1.x+p2.x)/2,(p1.y+p2.y)/2,canvas)
  }else{
    if(state.mode==="line"){
      ctx.beginPath()
      ctx.moveTo(p1.x,p1.y);ctx.lineTo(p2.x,p2.y);ctx.stroke()
      if(state.scaleValue>0) text=`長度: ${(pixD*state.scaleValue).toFixed(2)} ${state.unit}`
      else text=`長度: ${pixD.toFixed(1)} px`
      drawText(ctx,text,(p1.x+p2.x)/2,(p1.y+p2.y)/2,canvas)
    }else{
      const r=Math.hypot(p2.x-p1.x,p2.y-p1.y)/2
      ctx.beginPath()
      ctx.arc((p1.x+p2.x)/2,(p1.y+p2.y)/2,r,0,Math.PI*2)
      ctx.stroke()
      if(state.scaleValue>0) text=`直徑: ${(pixD*state.scaleValue).toFixed(2)} ${state.unit}`
      else text=`直徑: ${pixD.toFixed(1)} px`
      drawText(ctx,text,(p1.x+p2.x)/2,(p1.y+p2.y)/2,canvas)
    }
  }
}
}
function drawText(ctx,text,x,y,canvas){
  ctx.font="14px Arial"
  const metrics=ctx.measureText(text)
  const w=metrics.width+8
  const h=18
  const bg="rgba(0,0,0,0.6)"
  const fg="#fff"
  ctx.fillStyle=bg
  ctx.fillRect(x-w/2,y-h/2,w,h)
  ctx.fillStyle=fg
  ctx.textAlign="center"
  ctx.textBaseline="middle"
  ctx.fillText(text,x,y)
}
function updateDistLabels(){
  if(state.pointsA.length===2){
    const dx=Math.abs(state.pointsA[1].x-state.pointsA[0].x)
    const dy=Math.abs(state.pointsA[1].y-state.pointsA[0].y)
    if(state.scaleValue>0){
      el.distX().textContent=`水平距離: ${(dx*state.scaleValue).toFixed(4)} ${state.unit} | Horiz Dist: ${(dx*state.scaleValue).toFixed(4)} ${state.unit}`
      el.distY().textContent=`垂直距離: ${(dy*state.scaleValue).toFixed(4)} ${state.unit} | Vert Dist: ${(dy*state.scaleValue).toFixed(4)} ${state.unit}`
    }else{
      el.distX().textContent=`水平距離: ${dx.toFixed(1)} px | Horiz Dist: ${dx.toFixed(1)} px`
      el.distY().textContent=`垂直距離: ${dy.toFixed(1)} px | Vert Dist: ${dy.toFixed(1)} px`
    }
  }else{
    el.distX().textContent=`水平距離: --- | Horiz Dist: ---`
    el.distY().textContent=`垂直距離: --- | Vert Dist: ---`
  }
}
function setMode(val){
  state.mode=val
  redrawA()
  updateDistLabels()
}
function zoomInA(){state.zoomA=state.zoomA*1.2; redrawA()}
function zoomOutA(){state.zoomA=Math.max(0.05,state.zoomA/1.2); redrawA()}
function zoomResetA(){state.zoomA=1.0; redrawA()}
function zoomInB(){state.zoomB=state.zoomB*1.2; redrawB()}
function zoomOutB(){state.zoomB=Math.max(0.05,state.zoomB/1.2); redrawB()}
function zoomResetB(){state.zoomB=1.0; redrawB()}
function setScale(){
  if(state.pointsB.length!==2){
    log("請在尺規圖片(B)上選兩點 | Select 2 points on B")
    return
  }
  const v=parseFloat(el.actualDist().value)
  if(isNaN(v)||v<=0){log("無效距離 | Invalid distance");return}
  const dx=state.pointsB[1].x-state.pointsB[0].x
  const dy=state.pointsB[1].y-state.pointsB[0].y
  const pixD=Math.hypot(dx,dy)
  if(pixD<1e-6){el.scaleDisplay().textContent="比例尺: 無效 | Scale: Invalid";state.scaleValue=0;return}
  state.scaleValue=v/pixD
  state.unit=el.unitSel().value
  el.scaleDisplay().textContent=`比例尺: ${state.scaleValue.toFixed(6)} ${state.unit}/px | Scale: ${state.scaleValue.toFixed(6)} ${state.unit}/px`
  log(`比例尺已設: 1px ≈ ${state.scaleValue.toFixed(4)} ${state.unit}`)
  redrawA()
  updateDistLabels()
}
function resetAll(){
  state.scaleValue=0
  state.unit="mm"
  state.pointsA=[]
  state.pointsB=[]
  el.scaleDisplay().textContent="比例尺: 未設定 | Scale: Not Set"
  el.pointsA().textContent="已選點 (A): 0 | Selected Points (A): 0"
  el.pointsB().textContent="已選點 (B): 0 | Selected Points (B): 0"
  updateDistLabels()
  redrawA()
  redrawB()
}
function clearA(){
  state.pointsA=[]
  el.pointsA().textContent="已選點 (A): 0 | Selected Points (A): 0"
  updateDistLabels()
  redrawA()
  log("清除點 (A) | Cleared points (A)")
}
function clearB(){
  state.pointsB=[]
  el.pointsB().textContent="已選點 (B): 0 | Selected Points (B): 0"
  redrawB()
  log("清除點 (B) | Cleared points (B)")
}
function handleFile(file,cb){
  const img=new Image()
  img.onload=()=>cb(img)
  const url=URL.createObjectURL(file)
  img.src=url
}
function init(){
  el.modeInputs().forEach(i=>i.addEventListener('change',e=>setMode(e.target.value)))
  el.unitSel().addEventListener('change',e=>{state.unit=e.target.value;updateDistLabels();redrawA()})
  el.setScaleBtn().addEventListener('click',setScale)
  el.resetBtn().addEventListener('click',resetAll)
  el.clearA().addEventListener('click',clearA)
  el.clearB().addEventListener('click',clearB)
  el.zoomInA().addEventListener('click',zoomInA)
  el.zoomOutA().addEventListener('click',zoomOutA)
  el.zoomResetA().addEventListener('click',zoomResetA)
  el.zoomInB().addEventListener('click',zoomInB)
  el.zoomOutB().addEventListener('click',zoomOutB)
  el.zoomResetB().addEventListener('click',zoomResetB)
  el.fileA().addEventListener('change',e=>{
    const f=e.target.files[0]; if(!f)return
    handleFile(f,(img)=>{state.imgA=img;state.pointsA=[];state.zoomA=1.0;el.pointsA().textContent="已選點 (A): 0 | Selected Points (A): 0";redrawA();log("已加載圖片 (A) | Loaded image (A)")})
  })
  el.fileB().addEventListener('change',e=>{
    const f=e.target.files[0]; if(!f)return
    handleFile(f,(img)=>{state.imgB=img;state.pointsB=[];state.zoomB=1.0;el.pointsB().textContent="已選點 (B): 0 | Selected Points (B): 0";redrawB();log("已加載尺規圖片 (B) | Loaded ruler (B)")})
  })
  el.canvasA().addEventListener('mousemove',e=>{
    if(!state.imgA||!dispA){el.coordA().textContent="鼠標坐標 (A): 未加載 | Mouse Coords (A): Not loaded";return}
    const rect=el.canvasA().getBoundingClientRect()
    const cx=e.clientX-rect.left,cy=e.clientY-rect.top
    const p=canvasToImgCoord(cx,cy,dispA)
    const unit=state.scaleValue>0?state.unit:"px"
    el.coordA().textContent=`鼠標坐標 (A): (${p.x.toFixed(1)}, ${p.y.toFixed(1)}) (${unit}) | Mouse Coords (A)`
  })
  el.canvasA().addEventListener('click',e=>{
    if(!state.imgA||!dispA)return
    if(state.pointsA.length>=2)state.pointsA=[]
    const rect=el.canvasA().getBoundingClientRect()
    const cx=e.clientX-rect.left,cy=e.clientY-rect.top
    const p=canvasToImgCoord(cx,cy,dispA)
    const x=Math.max(0,Math.min(p.x,state.imgA.width))
    const y=Math.max(0,Math.min(p.y,state.imgA.height))
    state.pointsA.push({x,y})
    el.pointsA().textContent=`已選點 (A): ${state.pointsA.length} | Selected Points (A): ${state.pointsA.length}`
    redrawA()
    updateDistLabels()
  })
  el.canvasB().addEventListener('click',e=>{
    if(!state.imgB||!dispB)return
    if(state.pointsB.length>=2)state.pointsB=[]
    const rect=el.canvasB().getBoundingClientRect()
    const cx=e.clientX-rect.left,cy=e.clientY-rect.top
    const p=canvasToImgCoord(cx,cy,dispB)
    const x=Math.max(0,Math.min(p.x,state.imgB.width))
    const y=Math.max(0,Math.min(p.y,state.imgB.height))
    state.pointsB.push({x,y})
    el.pointsB().textContent=`已選點 (B): ${state.pointsB.length} | Selected Points (B): ${state.pointsB.length}`
    redrawB()
    if(state.pointsB.length===2)log("請輸入實際距離並設定比例尺 | Enter actual distance and set scale")
  })
  log("Application started")
  enableDragScroll(el.wrapA())
  enableDragScroll(el.wrapB())
}
window.addEventListener('load',init)
function enableDragScroll(wrapper){
  let isDown=false,startX=0,startY=0,scrollL=0,scrollT=0
  wrapper.addEventListener('mousedown',e=>{isDown=true;startX=e.pageX;startY=e.pageY;scrollL=wrapper.scrollLeft;scrollT=wrapper.scrollTop})
  window.addEventListener('mouseup',()=>{isDown=false})
  window.addEventListener('mousemove',e=>{
    if(!isDown)return
    const dx=e.pageX-startX
    const dy=e.pageY-startY
    wrapper.scrollLeft=scrollL-dx
    wrapper.scrollTop=scrollT-dy
  })
}
