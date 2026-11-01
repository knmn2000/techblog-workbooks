// catalog.js - the function components that the scenario files use.
//
// makeCatalog(lib, log) returns an object {ComponentName: function}. `lib` supplies createElement,
// useState and useEffect (your Didact in the assignments, React in the oracle); the hooks are looked up
// when a component renders, so the catalog can be built for a library that has no hooks yet. `log(text)`
// records one line for the scenario command `log`.
//
// The components are tiny on purpose. Ids are fixed so that scenarios can click them.

export function makeCatalog(lib, log) {
  const h = (...args) => lib.createElement(...args);
  const useState = (initial) => lib.useState(initial);
  const useEffect = (...args) => lib.useEffect(...args);

  // props.children is an array in Didact, but React passes a lone child as is
  const asList = (children) => (children === undefined || children === null ? [] : [].concat(children));

  // The setter of the first Keeper that ever rendered; the `poke` command calls it.
  let keeperSetter = null;

  function Greeting({ name }) {
    return h("h1", null, "Hi ", name);
  }

  function Frame({ title, children }) {
    return h("section", null, h("h2", null, title), ...asList(children));
  }

  function Counter({ id = "c", start = 0 }) {
    const [count, setCount] = useState(Number(start));
    // The handler always uses the updater form (c => c + 1), never the value it saw when it rendered.
    // The counter with id "d" calls the setter twice in one handler, so two updaters are queued in a
    // single event: each click must add 2. Assignment 10 uses it to test queued updaters.
    const onClick =
      id === "d"
        ? () => {
            setCount((c) => c + 1);
            setCount((c) => c + 1);
          }
        : () => setCount((c) => c + 1);
    return h("div", { id }, h("button", { id: id + "-inc", onClick }, "+"), h("span", { id: id + "-count" }, count));
  }

  function MultiCounter() {
    const [a, setA] = useState(0);
    const [b, setB] = useState(0);
    return h(
      "div",
      { id: "mc" },
      h("button", { id: "mc-a", onClick: () => setA((n) => n + 1) }, "a"),
      h("button", { id: "mc-b", onClick: () => setB((n) => n + 1) }, "b"),
      h("span", { id: "mc-av" }, a),
      h("span", { id: "mc-bv" }, b),
    );
  }

  // The root tag changes between renders: section (on) and div (off).
  function Toggle() {
    const [on, setOn] = useState(false);
    const button = h("button", { id: "t-btn", onClick: () => setOn((v) => !v) }, "toggle");
    const state = h("span", { id: "t-state" }, on ? "on" : "off");
    return on ? h("section", { id: "t", className: "on" }, button, state) : h("div", { id: "t" }, button, state);
  }

  function Keeper() {
    const [n, setN] = useState(0);
    keeperSetter ??= setN;
    return h("p", { id: "keeper" }, n);
  }

  function FnA() {
    return h("i", null, "a");
  }

  function FnB() {
    return h("b", null, "b");
  }

  function Logger({ name }) {
    useEffect(() => {
      log("mount " + name);
      return () => log("cleanup " + name);
    }, []);
    return h("em", null, name);
  }

  function LoggerDeps({ name, dep }) {
    useEffect(() => {
      log(`run ${name} ${dep}`);
      return () => log(`clean ${name} ${dep}`);
    }, [dep]);
    return h("em", null, name, ":", dep);
  }

  function LoggerEvery({ name }) {
    const [count, setCount] = useState(0);
    useEffect(() => {
      log("run " + name);
      return () => log("clean " + name);
    });
    return h(
      "div",
      null,
      h("em", null, name, ":", count),
      h("button", { id: name + "-btn", onClick: () => setCount((c) => c + 1) }, "bump"),
    );
  }

  function Outer({ name }) {
    useEffect(() => {
      log("mount " + name);
      return () => log("cleanup " + name);
    }, []);
    return h("div", null, h(Logger, { name: name + ".inner" }));
  }

  const catalog = { Greeting, Frame, Counter, MultiCounter, Toggle, Keeper, FnA, FnB, Logger, LoggerDeps, LoggerEvery, Outer };

  // Not a component: what the `poke` command calls. Calls the first Keeper's setter with n => n + 1.
  Object.defineProperty(catalog, "poke", {
    enumerable: false,
    value() {
      if (keeperSetter === null) throw new Error("poke: no Keeper has rendered yet");
      keeperSetter((n) => n + 1);
    },
  });

  return catalog;
}
