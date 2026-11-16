// A pane's header, for layouts that frame their panes:
//   { "tab": "active", "pane": { "header": { "content": { "mod": "ck-pane" } } } }
// Shows the program's icon (the app's program table), the agent's name or
// the terminal's title, the folder, and the agent's status; buttons split, zoom and close
// this pane. Props from the app: { pane, terminal }. Click: focus the pane.

import { View, div, svg, image } from "gpui-kit";
import { h_flex } from "gpui-base";
import { panes, terminals, props, run, theme, home, layout } from "herdr";

// CK status circles (the owner 2026-11-15): green = done, yellow = needs you, red = failed; a spinner while working.
// Live hc status first (error, blocked, working), then ck-herdr's final label ck.state (it stays after you look;
// Herdr's own "done" turns "idle" then), then Herdr's done.
const CK = { done: "#3fb950", needs: "#e3b341", failed: "#f85149" };
// One rule for every CK circle (the owner 2026-11-15: "I need those to be consistent"):
// spinner = working, green = finished, yellow = needs you, red = failed.
// ck-run's label ck.state (working at launch, done/needs/failed at the end) is the truth for its panes;
// live agent status only adds what the label cannot know (working again on a follow-up, blocked).
function ckCore(tm, st) {
  if (!tm && !st) return null;
  const raw = typeof tm?.status === "string" ? tm.status : tm?.status?.state;
  const lab = tm?.labels?.["ck.state"];
  const live = tm?.state !== "finished";
  if (raw === "error") return "failed";
  if (lab === "failed") return "failed";
  if (lab === "needs" || (live && (st === "blocked" || raw === "blocked"))) return "needs";
  if (live && (st === "working" || raw === "working")) return "working";
  if (lab === "done") return "done";
  if (st === "done" || raw === "done") return "done";
  if ((st === "idle" || raw === "idle" || !st) && (tm?.turn ?? 0) > 0) return "done";
  if (lab === "working" && live) return "working";
  return null;
}
function ckState(p, terms) {
  if (!p?.terminal) return null;
  return ckCore(terms.find(x => x.address === p.terminal), p.status);
}


// Match the first visible tab frame, including the active child of a stack.
function paneFrame(node) {
  if (!node || node.hidden) return null;
  if (node.content?.tab && node.content.pane) return node.content.pane;
  let children = node.children ?? [];
  if (node.type === "stack") {
    const visible = children.filter(child => !child.hidden);
    children = [visible.find(child => child.id === node.active) ?? visible[0]];
  }
  for (const child of children) {
    const frame = paneFrame(child);
    if (frame) return frame;
  }
  return null;
}

function icon(p, size, color) {
  if (!p?.icon) return null;
  return p.tint ? svg(p.icon).size(size).flex_none().text_color(color) : image(p.icon).w(size).h(size).flex_none();
}

function folder(cwd) {
  if (!cwd) return "";
  const h = home();
  return cwd === h ? "~" : cwd.startsWith(h + "/") ? "~" + cwd.slice(h.length) : cwd;
}

export default class Pane extends View {
  init() { this.hovered = false; }

  me() {
    return panes().find((p) => p.pane === props()?.pane);
  }

  button(t, id, icon, command, args) {
    return div()
      .id(id)
      .p(3)
      .rounded(4)
      .text_color(t.dim)
      .hover((s) => s.bg(t.hover).text_color(t.foreground))
      .on_click((_e, cx) => {
        cx.stop_propagation();
        run(command, args);
      })
      .child(svg(`mods/ck-pane/${icon}.svg`).size(14));
  }

  render(cx) {
    const t = theme();
    const p = this.me();
    if (!p) return div();
    const name = ((p.program?.agent || p.program?.shell) && p.program.name) || p.title || p.program?.name || "shell";
    // ck-run's short job description (label ck.title, the owner 2026-11-15): see at a glance what the agent is for.
    const job = terminals().find(x => x.address === p.terminal)?.labels?.["ck.title"];
    const pic = icon(p.program, 14, t.dim);
    const ck = ckState(p, terminals());
    const pane = p.pane;
    const bottom = paneFrame(layout())?.header?.position === "bottom";
    return h_flex()
      .id(`pane-head-${pane}`)
      .size_full()
      .px(10)
      .gap(8)
      .items_center()
      .bg(t.background)
      .when(bottom, el => el.border_t(1))
      .when(!bottom, el => el.border_b(1))
      .border_color(t.border)
      .text_size(12)
      .on_hover((hovered, cx) => { this.hovered = hovered; cx.notify(); })
      .on_click(() => run("pane.focus", { pane }))
      .when(Boolean(pic), (el) => el.child(pic))
      .child(div().flex_none().truncate().max_w(260).font_medium().text_color(t.foreground).child(name))
      .when(Boolean(job), el => el.child(div().flex_none().truncate().max_w(320).px(6).h(18).flex().items_center().rounded(5).bg(t.raised ?? t.hover).text_size(11).text_color(t.foreground).child(job)))
      .child(div().flex_1().truncate().text_color(t.dim).child(folder(p.cwd)))
      .when(ck === "working", el => el.child(svg("mods/workspace-chrome/spinner.svg").size(12).flex_none().text_color(t.working).spin(900)))
      .when(ck === "needs", el => el.child(div().flex_none().px(6).h(18).flex().items_center().rounded(5).bg(CK.needs + "26").text_size(10.5).font_semibold().text_color(CK.needs).child("Needs you")))
      .when(ck === "failed", el => el.child(div().flex_none().px(6).h(18).flex().items_center().rounded(5).bg(CK.failed + "26").text_size(10.5).font_semibold().text_color(CK.failed).child("Failed")))
      .when(ck === "done" || ck === "needs" || ck === "failed", el => el.child(div().size(10).flex_none().rounded(5).bg(CK[ck])))
      .when(this.hovered, el => el
        .child(this.button(t, `ph-r-${pane}`, "split-right", "pane.split", { direction: "right", pane }))
        .child(this.button(t, `ph-d-${pane}`, "split-down", "pane.split", { direction: "down", pane }))
        .child(this.button(t, `ph-z-${pane}`, p.zoomed ? "unzoom" : "zoom", "pane.zoom", { pane }))
        .child(this.button(t, `ph-x-${pane}`, "close", "pane.close", { pane })));
  }
}
