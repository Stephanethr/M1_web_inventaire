import confetti from 'canvas-confetti';
export const wrapConfetti = () => 
  {
  var scalar = 4;
  var unicorn = confetti.shapeFromText({ text: '🐍', scalar });
  
  var defaults = {
    spread: 550,
    ticks: 200,
    gravity: 2,
    decay: 0.96,
    startVelocity: 50,
    shapes: [unicorn],
    scalar,
    origin: { y: -1 }
  };
  
  function shoot() {
    confetti({
      ...defaults,
      particleCount: 200
    });
  }
  
  setTimeout(shoot, 0);
  setTimeout(shoot, 100);
  setTimeout(shoot, 200);
}
