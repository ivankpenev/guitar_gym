import SwiftUI

/// A visual representation of the guitar fretboard.
/// Highlights specific positions and optionally labels them.
struct FretboardView: View {
    let highlights: [FretHighlight]
    let fretRange: ClosedRange<Int>

    init(highlights: [FretHighlight] = [], fretRange: ClosedRange<Int> = 0...12) {
        self.highlights = highlights
        self.fretRange = fretRange
    }

    // Layout constants
    private let stringSpacing: CGFloat = 28
    private let fretWidth: CGFloat = 50

    // Standard fret markers
    private let markerFrets = [3, 5, 7, 9, 12, 15, 17, 19, 21, 24]
    private let doubleMarkerFrets = [12, 24]

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            ZStack(alignment: .topLeading) {
                // Fret lines
                ForEach(Array(fretRange), id: \.self) { fret in
                    Rectangle()
                        .fill(fret == 0 ? Color.primary : Color.gray.opacity(0.4))
                        .frame(width: fret == 0 ? 4 : 2, height: stringSpacing * 5)
                        .offset(x: CGFloat(fret - fretRange.lowerBound) * fretWidth, y: 0)
                }

                // Strings (horizontal lines)
                ForEach(0..<6) { stringIndex in
                    Rectangle()
                        .fill(Color.gray)
                        .frame(height: stringIndex < 3 ? 1 : CGFloat(stringIndex - 1))
                        .frame(width: CGFloat(fretRange.count) * fretWidth)
                        .offset(y: CGFloat(stringIndex) * stringSpacing)
                }

                // Fret markers (dots)
                ForEach(markerFrets.filter { fretRange.contains($0) }, id: \.self) { fret in
                    let x = (CGFloat(fret - fretRange.lowerBound) - 0.5) * fretWidth
                    if doubleMarkerFrets.contains(fret) {
                        // Double dot
                        Circle()
                            .fill(Color.gray.opacity(0.3))
                            .frame(width: 10, height: 10)
                            .offset(x: x, y: stringSpacing * 1.5)
                        Circle()
                            .fill(Color.gray.opacity(0.3))
                            .frame(width: 10, height: 10)
                            .offset(x: x, y: stringSpacing * 3.5)
                    } else {
                        Circle()
                            .fill(Color.gray.opacity(0.3))
                            .frame(width: 10, height: 10)
                            .offset(x: x, y: stringSpacing * 2.5)
                    }
                }

                // Highlighted positions
                ForEach(highlights) { highlight in
                    let stringY = CGFloat(6 - highlight.string) * stringSpacing
                    let fretX: CGFloat = highlight.fret == 0
                        ? -fretWidth * 0.3
                        : (CGFloat(highlight.fret - fretRange.lowerBound) - 0.5) * fretWidth

                    ZStack {
                        Circle()
                            .fill(highlight.color)
                            .frame(width: 24, height: 24)
                        if let label = highlight.label {
                            Text(label)
                                .font(.caption2.bold())
                                .foregroundColor(.white)
                        }
                    }
                    .offset(x: fretX, y: stringY - 12)
                }

                // Fret numbers along bottom
                ForEach(Array(fretRange), id: \.self) { fret in
                    if fret > 0 {
                        Text("\(fret)")
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                            .offset(
                                x: (CGFloat(fret - fretRange.lowerBound) - 0.5) * fretWidth - 4,
                                y: stringSpacing * 5 + 8
                            )
                    }
                }
            }
            .padding()
            .frame(height: stringSpacing * 5 + 40)
        }
    }
}

struct FretHighlight: Identifiable {
    let id = UUID()
    let string: Int  // 1-6
    let fret: Int    // 0-24
    let label: String?
    let color: Color

    init(string: Int, fret: Int, label: String? = nil, color: Color = .blue) {
        self.string = string
        self.fret = fret
        self.label = label
        self.color = color
    }
}
