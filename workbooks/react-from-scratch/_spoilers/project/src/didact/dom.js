// Assignment 02: the two places the library touches a real DOM node.

const isEvent = (name) => name.startsWith('on');
const isProperty = (name) => name !== 'children' && name !== 'key' && !isEvent(name);
const eventType = (name) => name.toLowerCase().substring(2); // onClick -> click

export function createDom(element) {
  const dom =
    element.type === 'TEXT_ELEMENT' ? document.createTextNode('') : document.createElement(element.type);
  updateDom(dom, {}, element.props);
  return dom;
}

// Brings dom in line with nextProps and touches only what differs from prevProps.
export function updateDom(dom, prevProps, nextProps) {
  const isNew = (name) => prevProps[name] !== nextProps[name];
  const isGone = (name) => !(name in nextProps);
  const prevNames = Object.keys(prevProps);
  const nextNames = Object.keys(nextProps);

  // A changed handler is a different function, so the old one has to come off first.
  for (const name of prevNames.filter(isEvent)) {
    if (isGone(name) || isNew(name)) dom.removeEventListener(eventType(name), prevProps[name]);
  }
  for (const name of prevNames.filter(isProperty)) {
    if (isGone(name)) dom[name] = '';
  }
  for (const name of nextNames.filter(isProperty)) {
    if (isNew(name)) dom[name] = nextProps[name];
  }
  for (const name of nextNames.filter(isEvent)) {
    if (isNew(name)) dom.addEventListener(eventType(name), nextProps[name]);
  }
}
