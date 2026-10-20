#pragma once

#include <stdexcept>
#include <string>

// Thrown by the starter stubs. The test runner recognises it and tells you
// which function is still waiting to be written.
struct NotImplemented : std::logic_error {
  explicit NotImplemented(const std::string& function) : std::logic_error(function) {}
};
