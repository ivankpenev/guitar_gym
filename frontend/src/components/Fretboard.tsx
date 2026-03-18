import React from "react";
import { ScrollView, StyleSheet, View, Text as RNText } from "react-native";
import Svg, { Line, Circle, Rect, Text as SvgText } from "react-native-svg";

interface Highlight {
  string: number; // 1-6
  fret: number; // 0-24
  label?: string;
  color?: string;
}

interface FretboardProps {
  highlights?: Highlight[];
  fretRange?: [number, number]; // [min, max] inclusive
}

const STRING_COUNT = 6;
const FRET_WIDTH = 56;
const STRING_SPACING = 30;
const TOP_PADDING = 24;
const BOTTOM_PADDING = 24;
const LEFT_PADDING = 36;
const NUT_WIDTH = 4;

const FRET_MARKER_FRETS = [3, 5, 7, 9, 12, 15, 17, 19, 21, 24];
const DOUBLE_DOT_FRETS = [12, 24];

const STRING_LABELS = ["E", "B", "G", "D", "A", "E"];

export default function Fretboard({ highlights = [], fretRange }: FretboardProps) {
  // Auto-calculate fret range from highlights if not given
  let minFret = fretRange?.[0] ?? 0;
  let maxFret = fretRange?.[1] ?? 12;
  if (!fretRange && highlights.length > 0) {
    const frets = highlights.map((h) => h.fret);
    const lo = Math.min(...frets);
    const hi = Math.max(...frets);
    minFret = Math.max(0, lo - 2);
    maxFret = Math.min(24, hi + 2);
    if (maxFret - minFret < 5) maxFret = Math.min(24, minFret + 5);
  }

  const visibleFrets = maxFret - minFret;
  const svgWidth = LEFT_PADDING + NUT_WIDTH + visibleFrets * FRET_WIDTH + 20;
  const svgHeight = TOP_PADDING + (STRING_COUNT - 1) * STRING_SPACING + BOTTOM_PADDING;

  const fretX = (fret: number) =>
    LEFT_PADDING + NUT_WIDTH + (fret - minFret) * FRET_WIDTH;
  const stringY = (str: number) =>
    TOP_PADDING + (str - 1) * STRING_SPACING; // string 1 = top (high E)

  return (
    <View style={styles.container}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <Svg width={svgWidth} height={svgHeight}>
          {/* Nut */}
          {minFret === 0 && (
            <Rect
              x={LEFT_PADDING}
              y={TOP_PADDING - 2}
              width={NUT_WIDTH}
              height={(STRING_COUNT - 1) * STRING_SPACING + 4}
              fill="#e0e0e0"
            />
          )}

          {/* Fret lines */}
          {Array.from({ length: visibleFrets + 1 }, (_, i) => {
            const fret = minFret + i;
            if (fret === 0) return null;
            const x = fretX(fret);
            return (
              <Line
                key={`fret-${fret}`}
                x1={x}
                y1={TOP_PADDING - 2}
                x2={x}
                y2={stringY(STRING_COUNT) + 2}
                stroke="#555"
                strokeWidth={1.5}
              />
            );
          })}

          {/* Fret numbers */}
          {Array.from({ length: visibleFrets + 1 }, (_, i) => {
            const fret = minFret + i;
            if (fret === 0) return null;
            return (
              <SvgText
                key={`fn-${fret}`}
                x={fretX(fret) - FRET_WIDTH / 2}
                y={svgHeight - 4}
                fontSize={10}
                fill="#888"
                textAnchor="middle"
              >
                {fret}
              </SvgText>
            );
          })}

          {/* Fret marker dots */}
          {FRET_MARKER_FRETS.filter(
            (f) => f > minFret && f <= maxFret
          ).map((f) => {
            const cx = fretX(f) - FRET_WIDTH / 2;
            if (DOUBLE_DOT_FRETS.includes(f)) {
              return (
                <React.Fragment key={`dot-${f}`}>
                  <Circle cx={cx} cy={stringY(2)} r={4} fill="#333" />
                  <Circle cx={cx} cy={stringY(5)} r={4} fill="#333" />
                </React.Fragment>
              );
            }
            return (
              <Circle
                key={`dot-${f}`}
                cx={cx}
                cy={stringY(3) + STRING_SPACING / 2}
                r={4}
                fill="#333"
              />
            );
          })}

          {/* Strings */}
          {Array.from({ length: STRING_COUNT }, (_, i) => {
            const str = i + 1;
            const y = stringY(str);
            // Thicker strings for lower pitched
            const thickness = 0.8 + (str <= 3 ? 0 : (str - 3) * 0.4);
            return (
              <Line
                key={`str-${str}`}
                x1={LEFT_PADDING}
                y1={y}
                x2={svgWidth - 10}
                y2={y}
                stroke="#bbb"
                strokeWidth={thickness}
              />
            );
          })}

          {/* String labels */}
          {STRING_LABELS.map((label, i) => (
            <SvgText
              key={`sl-${i}`}
              x={10}
              y={stringY(i + 1) + 4}
              fontSize={12}
              fill="#888"
              fontWeight="bold"
              textAnchor="middle"
            >
              {label}
            </SvgText>
          ))}

          {/* Highlights */}
          {highlights.map((h, idx) => {
            const cx =
              h.fret === 0
                ? LEFT_PADDING - 10
                : fretX(h.fret) - FRET_WIDTH / 2;
            const cy = stringY(h.string);
            const color = h.color || "#4f9cf7";
            return (
              <React.Fragment key={`hl-${idx}`}>
                <Circle cx={cx} cy={cy} r={12} fill={color} />
                {h.label && (
                  <SvgText
                    x={cx}
                    y={cy + 4}
                    fontSize={11}
                    fill="#fff"
                    fontWeight="bold"
                    textAnchor="middle"
                  >
                    {h.label}
                  </SvgText>
                )}
              </React.Fragment>
            );
          })}
        </Svg>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#1e1e2e",
    borderRadius: 12,
    paddingVertical: 8,
    marginVertical: 12,
  },
});
