#include "font/Metrics.h"

#include <stdexcept>

HorizontalMetrics loadHorizontalMetrics(ByteReader& reader, const Tables& tables) {
  // TODO: ascent, descent and numberOfHMetrics from hhea, then hmtx (see the problem page).
  throw std::logic_error("not implemented: loadHorizontalMetrics");
}
