from xml.sax.saxutils import XMLGenerator
from contextlib import contextmanager
from . import base
from math import sin, cos, radians
from collections import Iterable

class Renderer(base.Renderer):
    def __init__(self, size, units, unitmult=1, *, margin=0,
    down=+1,  # -1 if y axis points upwards
    line=None, textsize=None, textbottom=False):
        width = size[0] + 2 * margin
        height = size[1] + 2 * margin
        if down < 0:
            top = -size[1]
            self.flip = (+1, -1)
        else:
            top = 0
            self.flip = (+1, +1)
        viewbox = "{},{} {},{}".format(-margin, top - margin, width, height)
        
        self.xml = XMLGenerator(encoding="UTF-8", short_empty_elements=True)
        self.xml.startElement("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
            "width": "{}{}".format(width * unitmult, units),
            "height": "{}{}".format(height * unitmult, units),
            "viewBox": viewbox,
        })
        
        outline = ["stroke: currentColor", "fill: none"]
        if line is not None:
            outline.append("stroke-width: {}".format(line))
        
        text = list()
        if textsize is not None:
            text.append("font-size: {}px".format(textsize))
        if textbottom:
            text.append("dominant-baseline: text-after-edge")
        text.append("fill: currentColor")
        
        self.rulesets = [
            (".outline, path, line, polyline", outline),
            (".solid", ("fill: currentColor", "stroke: none")),
            ("text", text),
        ]
    
    def addfont(self, id, size, family, italic=None, bold=None):
        props = [
            "font-size: {}px".format(size),
            "font-family: {}".format(family),
        ]
        if italic:
            props.append("font-style: italic")
        if bold:
            props.append("font-weight: bold")
        self.rulesets.append(("." + id, props))
    
    def start(self):
        css = list()
        for (selector, rules) in self.rulesets:
            rules = "".join(map("  {};\n".format, rules))
            css.append("{} {{\n{}}}\n".format(selector, rules))
        self.tree(("style", dict(type="text/css"), css))
    
    def finish(self):
        self.xml.endElement("svg")
    
    def line(self, a=None, b=None, *pos, **kw):
        attrs = dict()
        for (n, p) in enumerate((a, b), 1):
            if p:
                (x, y) = p
                attrs["x{}".format(n)] = format(x)
                attrs["y{}".format(n)] = format(y * self.flip[1])
        self._line(attrs, *pos, **kw)
    
    def hline(self, a=None, b=None, y=None, *pos, **kw):
        attrs = dict()
        if y is not None:
            y = format(y * self.flip[1])
            attrs.update(y1=y, y2=y)
        for (n, xn) in enumerate((a, b), 1):
            if xn is not None:
                attrs["x{}".format(n)] = format(xn)
        self._line(attrs, *pos, **kw)
    
    def vline(self, a=None, b=None, x=None, *pos, **kw):
        attrs = dict()
        if x is not None:
            x = format(x)
            attrs.update(x1=x, x2=x)
        for (n, yn) in enumerate((a, b), 1):
            if yn is not None:
                attrs["y{}".format(n)] = format(yn * self.flip[1])
        self._line(attrs, *pos, **kw)
    
    def _line(self, attrs, *, colour=None, **kw):
        style = list()
        self._width(style, **kw)
        attrs.update(self._colour(colour))
        self.emptyelement("line", attrs, style=style)
    
    def polyline(self, points, *, colour=None, **kw):
        s = list()
        for (x, y) in points:
            s.append("{},{}".format(x, y * self.flip[1]))
        attrs = {"points": " ".join(s)}
        style = list()
        self._width(style, **kw)
        attrs.update(self._colour(colour))
        self.emptyelement("polyline", attrs, style=style)
    
    def box(self, dim, start=None, *pos, **kw):
        attrs = {"class": "outline"}
        style = list()
        (w, h) = dim
        attrs["width"] = format(w)
        attrs["height"] = format(h)
        
        if self.flip[1] < 0:
            # Compensate for SVG not allowing negative height
            if start:
                (x, y) = start
            else:
                x = 0
                y = 0
            y += h
            start = (x, y)
        
        if start:
            (x, y) = start
            attrs["x"] = format(x)
            attrs["y"] = format(y * self.flip[1])
        self._width(style, *pos, **kw)
        self.emptyelement("rect", attrs, style=style)
    
    def circle(self, r, centre=None, *, outline=None, fill=None, width=None):
        attrs = {"r": format(r)}
        style = list()
        if fill:
            attrs["class"] = "solid"
            if isinstance(fill, Iterable):
                style.extend(self._colour(fill, "fill"))
        else:
            attrs["class"] = "outline"
        if isinstance(outline, Iterable):
            style.extend(self._colour(outline, "stroke"))
        if centre:
            (x, y) = centre
            attrs["cx"] = format(x)
            attrs["cy"] = format(y * self.flip[1])
        self._width(style, width)
        self.emptyelement("circle", attrs, style=style)
    
    def _width(self, style, width=None):
        if width is not None:
            style.append(("stroke-width", width))
    
    def polygon(self, points, *, colour=None):
        s = list()
        for (x, y) in points:
            s.append("{},{}".format(x, y * self.flip[1]))
        attrs = {"class": "solid", "points": " ".join(s)}
        attrs.update(self._colour(colour))
        self.emptyelement("polygon", attrs)
    
    def rectangle(self, dim, start=None):
        attrs = {"class": "solid"}
        attrs.update(zip(("width", "height"), map(format, dim)))
        if start:
            attrs.update(zip("xy", map(format, start)))
        self.emptyelement("rect", attrs)
    
    def arc(self, r, start, end, centre=None, *, colour=None):
        if abs(end - start) >= 360:
            attrs = {"r": format(*r), "class": "outline"}
            if point:
                (x, y) = point
                attrs["cx"] = format(x)
                attrs["cy"] = format(y * self.flip[1])
            attrs.update(self._colour(colour))
            renderer.emptyelement("circle", attrs)
        else:
            a = list()
            d = list()
            for x in range(2):
                sincos = (cos, sin)[x]
                da = sincos(radians(start))
                db = sincos(radians(end))
                a.append(format((centre[x] + da * r[x]) * self.flip[x]))
                d.append(format((db - da) * r[x] * self.flip[x]))
            large = (end - start) % 360 > 180
            at = dict(self._colour(colour))
            at["d"] = "M{a} a{r} 0 {large:d},0 {d}".format(
                a=",".join(a),
                r=",".join(map(format, r)),
                large=large,
                d=",".join(d),
            )
            self.emptyelement("path", at)
    
    def text(self, text, point=None, horiz=None, vert=None, *,
    angle=None, font=None, colour=None):
        attrs = dict()
        style = list()
        if vert is not None:
            baselines = {
                self.CENTRE: "middle",
                self.TOP: "text-before-edge",
                self.BOTTOM: "text-after-edge",
            }
            style.append(("dominant-baseline", baselines[vert]))
        if horiz is not None:
            anchors = {
                self.CENTRE: "middle",
                self.LEFT: "start",
                self.RIGHT: "end",
            }
            style.append(("text-anchor", anchors[horiz]))
        
        if point:
            (x, y) = point
            y *= self.flip[1]
        if angle is not None:
            transform = list()
            if point:
                transform.append("translate({}, {})".format(x, y))
            transform.append("rotate({})".format(angle))
            attrs["transform"] = " ".join(transform)
        elif point:
            attrs["x"] = format(x)
            attrs["y"] = format(y)
        
        if font is not None:
            attrs["class"] = font
        attrs.update(self._colour(colour))
        with self.element("text", attrs, style=style):
            self.xml.characters(text)
    
    def _colour(self, colour=None, attr="color"):
        if colour:
            colour = (min(int(x * 0x100), 0xFF) for x in colour)
            return ((attr, "#" + "".join(map("{:02X}".format, colour))),)
        else:
            return ()
    
    def addobjects(self, objects):
        with self.element("defs", dict()):
            for d in objects:
                with self.element("g", dict(id=d.__name__)):
                    d(self)
    
    def draw(self, object, offset=None):
        attrs = {"xlink:href": "#{}".format(object.__name__)}
        if offset:
            attrs.update(zip("xy", map(format, offset)))
        self.emptyelement("use", attrs)
    
    @contextmanager
    def offset(self, offset):
        (x, y) = offset
        translate = "translate({}, {})".format(x, y * self.flip[-1])
        with self.element("g", dict(transform=translate)):
            yield self
    
    @contextmanager
    def element(self, name, attrs=(), style=None):
        attrs = dict(attrs)
        if style:
            attrs["style"] = "; ".join("{}: {}".format(*s) for s in style)
        self.xml.startElement(name, attrs)
        yield
        self.xml.endElement(name)
    
    def emptyelement(self, *pos, **kw):
        with self.element(*pos, **kw):
            pass
    
    def tree(self, *elements):
        for e in elements:
            if isinstance(e, str):
                self.xml.characters(e)
            else:
                (name, attrs, children) = e
                with self.element(name, attrs):
                    self.tree(*children)
