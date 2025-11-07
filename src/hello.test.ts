import { hello } from "./hello";

describe("hello", () => {
  it("should return the correct greeting", () => {
    const result = hello();
    expect(result).toBe("Hello from Agent Cube!");
  });
});
