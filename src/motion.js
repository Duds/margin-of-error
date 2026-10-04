/* Motion. Implements the two animations DESIGN.md specifies, nothing else.
 *
 *   fade-in  240ms  section entry, once, on intersection
 *   draw     600ms  line chart path draw, once, on intersection
 *
 * No library. Measured at 0.4KB gzipped against 16KB for animejs. GSAP is
 * excluded on licence, since its npm grant is not an OSI open-source licence.
 *
 * Reduced motion is handled in CSS (see margin-of-error.css), so there is no
 * JS branch here that can get it wrong. This module only settles final state.
 */

const REDUCE = matchMedia("(prefers-reduced-motion: reduce)");

function show(el) {
  el.dataset.motionState = "shown";
}

/* Draw every path tagged for the draw treatment on an element. */
function drawPaths(el) {
  const paths = el.querySelectorAll("[data-draw-path]");
  if (!paths.length) return false;

  for (const path of paths) {
    /* pathLength=1 lets CSS use unitless offsets, so the animation does not
       depend on the path's own geometry. */
    path.style.strokeDasharray = "1";
    path.style.strokeDashoffset = "1";
  }

  el.dataset.motionState = "drawn";
  requestAnimationFrame(() => {
    for (const path of paths) path.style.strokeDashoffset = "0";
  });
  return true;
}

const targets = document.querySelectorAll("[data-motion], [data-draw]");

/* No IntersectionObserver, or nothing to animate: resolve to final state so
   content is never left invisible. */
if (!("IntersectionObserver" in window) || !targets.length) {
  for (const el of targets) show(el);
} else {
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const el = entry.target;
        observer.unobserve(el);

        if (REDUCE.matches) {
          show(el);
          continue;
        }

        /* A path draw wins over a plain fade. A line chart needs both, so the
           fade belongs on the figure wrapper and the draw on the SVG. */
        if (!drawPaths(el)) show(el);
      }
    },
    { rootMargin: "0px 0px -10% 0px", threshold: 0.1 }
  );

  for (const el of targets) observer.observe(el);
}

/* A late-arriving reduced-motion preference must settle everything already
   drawn, including paths the observer already handled. */
REDUCE.addEventListener("change", () => {
  if (!REDUCE.matches) return;
  for (const path of document.querySelectorAll("[data-draw-path]")) {
    path.style.transition = "none";
    path.style.strokeDashoffset = "0";
  }
  for (const el of document.querySelectorAll("[data-motion]")) show(el);
});
