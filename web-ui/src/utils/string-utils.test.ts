import { describe, it, expect } from "vitest";
import { capitalize, slugify } from "./string-utils";

describe("capitalize", () => {
  it("should capitalize the first letter of a lowercase word", () => {
    const input = "hello";

    const result = capitalize(input);

    expect(result).toBe("Hello");
  });

  it("should capitalize an all uppercase word", () => {
    const input = "WORLD";

    const result = capitalize(input);

    expect(result).toBe("World");
  });

  it("should lowercase the remaining characters in a mixed-case input", () => {
    const input = "hELLo WoRLD";

    const result = capitalize(input);

    expect(result).toBe("Hello world");
  });

  it("should return an empty string when input is empty", () => {
    const input = "";

    const result = capitalize(input);

    expect(result).toBe("");
  });

  it("should handle single-character strings", () => {
    const input = "a";

    const result = capitalize(input);

    expect(result).toBe("A");
  });

  it("should preserve surrounding whitespace", () => {
    const input = "  hello  ";

    const result = capitalize(input);

    expect(result).toBe("  hello  ");
  });

  it("should handle strings with numbers and special characters", () => {
    const input = "123abc$";

    const result = capitalize(input);

    expect(result).toBe("123abc$");
  });

  it("should support unicode characters", () => {
    const accentedInput = "éCLAIR";
    const emojiInput = "😊SMILE";

    const accentedResult = capitalize(accentedInput);
    const emojiResult = capitalize(emojiInput);

    expect(accentedResult).toBe("Éclair");
    expect(emojiResult).toBe("😊smile");
  });
});

describe("slugify", () => {
  it("should convert basic strings to slug format", () => {
    const input = "Hello World";

    const result = slugify(input);

    expect(result).toBe("hello-world");
  });

  it("should collapse multiple spaces into a single hyphen", () => {
    const input = "  Multiple   Spaces  ";

    const result = slugify(input);

    expect(result).toBe("multiple-spaces");
  });

  it("should remove special characters", () => {
    const input = "Special!@#$Characters";

    const result = slugify(input);

    expect(result).toBe("specialcharacters");
  });

  it("should retain numbers and lowercase letters", () => {
    const input = "Mix3d NUM83RS";

    const result = slugify(input);

    expect(result).toBe("mix3d-num83rs");
  });

  it("should handle uppercase input", () => {
    const input = "UPPERCASE";

    const result = slugify(input);

    expect(result).toBe("uppercase");
  });

  it("should return an empty string when input is empty", () => {
    const input = "";

    const result = slugify(input);

    expect(result).toBe("");
  });

  it("should remove leading and trailing hyphens", () => {
    const input = "---Hyphens---";

    const result = slugify(input);

    expect(result).toBe("hyphens");
  });

  it("should handle unicode characters with diacritics", () => {
    const input = "Árvíztűrő tükörfúrógép";

    const result = slugify(input);

    expect(result).toBe("arvizturo-tukorfurogep");
  });

  it("should return an empty slug when only special characters are provided", () => {
    const input = "@@@";

    const result = slugify(input);

    expect(result).toBe("");
  });

  it("should return an empty slug when only whitespace is provided", () => {
    const input = "   ";

    const result = slugify(input);

    expect(result).toBe("");
  });

  it("should be idempotent for already slugified strings", () => {
    const input = "already-slugified";

    const result = slugify(input);

    expect(result).toBe("already-slugified");
  });
});
