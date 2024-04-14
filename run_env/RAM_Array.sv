`timescale 1ns / 1ps

module RAM_Array #(
    parameter DATA_WIDTH = 32,
    parameter BYTE_ADDR_WIDTH = 8
) (
    input clk,
    input en,
    input wen,
    input [BYTE_ADDR_WIDTH-1:0] addr,
    input [DATA_WIDTH-1:0] din,
    output [DATA_WIDTH-1:0] dout
);
    reg [DATA_WIDTH-1:0] memory_cells [0:2**BYTE_ADDR_WIDTH-1];

    assign dout = memory_cells[addr];

    always @(posedge clk) begin
        if (en) begin
            if (wen) begin
                memory_cells[addr] = din;
            end
        end
    end
endmodule
