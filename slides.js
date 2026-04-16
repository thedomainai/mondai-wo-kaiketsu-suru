(function () {
  function createElement(tagName, className, textContent) {
    const element = document.createElement(tagName);
    if (className) {
      element.className = className;
    }
    if (textContent !== undefined) {
      element.textContent = textContent;
    }
    return element;
  }

  function prependLayer(container, element) {
    container.insertBefore(element, container.firstChild);
  }

  function syncBodyBackground(container) {
    const backgroundColor = getComputedStyle(container).backgroundColor;
    if (backgroundColor) {
      document.body.style.backgroundColor = backgroundColor;
    }
  }

  function renderStandardHeader(container) {
    if (!container.dataset.headerTitle || container.querySelector(".slide-standard-header")) {
      return;
    }

    const wrapper = createElement("div", "slide-standard-header");
    const band = createElement("div", "slide-standard-header__band");
    const brandWrap = createElement("div", "slide-standard-header__brand");
    const brandText = createElement(
      "p",
      "slide-standard-header__brand-text",
      container.dataset.headerBrand || "ロジカル・シンキング研修"
    );
    const copy = createElement("div", "slide-standard-header__copy");
    copy.classList.add("stack", "stack--left");
    const chapter = createElement(
      "p",
      "slide-standard-header__chapter",
      container.dataset.headerChapter || ""
    );
    const body = createElement("div", "slide-standard-header__body");
    const title = createElement(
      "p",
      "slide-standard-header__title",
      container.dataset.headerTitle || ""
    );
    const subtitle = createElement(
      "p",
      "slide-standard-header__subtitle",
      container.dataset.headerSubtitle || ""
    );

    brandWrap.appendChild(brandText);
    copy.appendChild(chapter);
    body.appendChild(title);
    if (subtitle.textContent) {
      body.appendChild(subtitle);
    }
    copy.appendChild(body);

    wrapper.appendChild(band);
    wrapper.appendChild(brandWrap);
    wrapper.appendChild(copy);
    container.appendChild(wrapper);

    fitText(title, copy.clientWidth, 28);
  }

  function renderStandardFooter(container) {
    const footerCompatibleKinds = new Set(["content", "intro", "center-title", "summary"]);
    if (
      container.dataset.footer !== "standard" ||
      container.querySelector(".slide-standard-footer") ||
      !footerCompatibleKinds.has(container.dataset.slideKind || "")
    ) {
      return;
    }

    const wrapper = createElement("div", "slide-standard-footer");
    const band = createElement("div", "slide-standard-footer__band");
    const brandWrap = createElement("div", "slide-standard-footer__brand");
    const brandText = createElement(
      "p",
      "slide-standard-footer__brand-text",
      container.dataset.footerBrand || "LOGICAL THINKING TRAINING"
    );

    brandWrap.appendChild(brandText);
    wrapper.appendChild(band);
    wrapper.appendChild(brandWrap);

    if (container.dataset.footerPage) {
      const pageWrap = createElement("div", "slide-standard-footer__page-wrap");
      const page = createElement("p", "slide-standard-footer__page", container.dataset.footerPage);
      pageWrap.appendChild(page);
      wrapper.appendChild(pageWrap);
    }

    container.appendChild(wrapper);
  }

  function renderGrainBackground(container) {
    if (container.dataset.background !== "grain" || container.querySelector(".slide-grain-layer")) {
      return;
    }

    const opacity = container.dataset.grainOpacity || "0.5";
    const grain = createElement("div", "slide-layer slide-grain-layer");
    grain.setAttribute("aria-hidden", "true");
    grain.innerHTML =
      '<svg width="1280" height="720" xmlns="http://www.w3.org/2000/svg">' +
      '<filter id="slide-grain-filter">' +
      '<feTurbulence type="fractalNoise" baseFrequency="0.5" numOctaves="3" stitchTiles="stitch"/>' +
      '<feColorMatrix type="saturate" values="0"/>' +
      '<feBlend in="SourceGraphic" mode="overlay"/>' +
      '<feComposite in2="SourceGraphic" operator="in"/>' +
      "</filter>" +
      '<rect width="1280" height="720" fill="#d8d8d8" filter="url(#slide-grain-filter)" opacity="' +
      opacity +
      '"/>' +
      "</svg>";
    prependLayer(container, grain);

    if (container.dataset.vignette !== "false") {
      const vignette = createElement("div", "slide-layer slide-vignette-layer");
      vignette.setAttribute("aria-hidden", "true");
      prependLayer(container, vignette);
    }
  }

  function renderHalftoneBackground(container) {
    if (container.dataset.background !== "halftone" || container.querySelector(".slide-halftone-canvas")) {
      return;
    }

    const canvas = createElement("canvas", "slide-layer slide-halftone-canvas");
    canvas.setAttribute("aria-hidden", "true");
    canvas.width = 1280;
    canvas.height = 720;
    prependLayer(container, canvas);

    const context = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;
    const grid = 18;
    const maxRadius = 3.2;
    const minRadius = 0.3;
    const origin = container.dataset.halftoneOrigin || "bottom-right";
    const strength = parseFloat(container.dataset.halftoneStrength || "1");

    for (let y = grid / 2; y < height; y += grid) {
      for (let x = grid / 2; x < width; x += grid) {
        const rawX = x / width;
        const rawY = y / height;
        const dx = origin === "bottom-left" ? 1 - rawX : rawX;
        const dy = rawY;
        const tone = Math.min(1, Math.pow(dx * 0.48 + dy * 0.48, 1.8) * strength);
        const radius = minRadius + (maxRadius - minRadius) * tone;
        const alpha = 0.018 + 0.06 * tone;
        context.beginPath();
        context.arc(x, y, radius, 0, Math.PI * 2);
        context.fillStyle = "rgba(0, 0, 0, " + alpha.toFixed(3) + ")";
        context.fill();
      }
    }
  }

  function renderDivider(container) {
    if (!container.dataset.dividerTitle || container.querySelector(".slide-divider")) {
      return;
    }

    const wrapper = createElement("div", "slide-divider");
    const brandWrap = createElement("div", "slide-divider__brand");
    const brandText = createElement(
      "p",
      "slide-divider__brand-text",
      container.dataset.dividerBrand || "ロジカル・シンキング研修"
    );
    const index = createElement(
      "p",
      "slide-divider__index",
      container.dataset.dividerIndex || ""
    );
    const copy = createElement("div", "slide-divider__copy");
    copy.classList.add("stack", "stack--center");
    const kicker = createElement(
      "p",
      "slide-divider__kicker",
      container.dataset.dividerKicker || ""
    );
    const body = createElement("div", "slide-divider__body");
    const title = createElement(
      "p",
      "slide-divider__title",
      container.dataset.dividerTitle || ""
    );
    const subtitle = createElement(
      "p",
      "slide-divider__subtitle",
      container.dataset.dividerSubtitle || ""
    );

    brandWrap.appendChild(brandText);
    copy.appendChild(kicker);
    body.appendChild(title);
    if (subtitle.textContent) {
      body.appendChild(subtitle);
    }
    copy.appendChild(body);

    wrapper.appendChild(brandWrap);
    wrapper.appendChild(index);
    wrapper.appendChild(copy);
    container.appendChild(wrapper);

    fitText(title, 920, 34);
  }

  function fitText(target, maxWidth, minSize) {
    if (!target || !maxWidth) {
      return;
    }

    let size = parseFloat(getComputedStyle(target).fontSize);
    const minimum = minSize || 40;

    target.style.whiteSpace = "nowrap";
    while (target.scrollWidth > maxWidth && size > minimum) {
      size -= 1;
      target.style.fontSize = size + "px";
    }

    if (target.scrollWidth > maxWidth) {
      target.style.whiteSpace = "normal";
      target.style.textWrap = "balance";
    }
  }

  function fitCenterSlideTitles(container) {
    if (!container.classList.contains("slide-center-title")) {
      return;
    }

    const title = container.querySelector(".title");
    const inner = container.querySelector(".inner");
    if (!title || !inner) {
      return;
    }

    fitText(title, inner.clientWidth, 40);
  }

  document.addEventListener("DOMContentLoaded", function () {
    const container = document.querySelector(".slide-container");
    if (!container) {
      return;
    }

    syncBodyBackground(container);
    renderGrainBackground(container);
    renderHalftoneBackground(container);
    renderDivider(container);
    renderStandardHeader(container);
    renderStandardFooter(container);
    fitCenterSlideTitles(container);
  });
})();
