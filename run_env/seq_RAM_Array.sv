`timescale 1ns / 1ps

module Seq_RAM_Array #(
    parameter DATA_WIDTH = 32,
    parameter BYTE_ADDR_WIDTH = 8
) (
    input clk,
    input en,
    input wen,
    input [BYTE_ADDR_WIDTH-1:0] addr,
    input [DATA_WIDTH-1:0] din,
    output reg [DATA_WIDTH-1:0] dout
);
    reg [DATA_WIDTH-1:0] memory_cells [0:2**BYTE_ADDR_WIDTH-1];

    always @(posedge clk) begin
        if (en) begin
            if (wen)
                memory_cells[addr] = din;
            else
                dout <= memory_cells[addr];
        end
    end
endmodule
