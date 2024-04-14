module switch #(
    parameter DATA_WIDTH = 16,
    parameter BYTE_ADDR_WIDTH = 8
) (
    input clk,
    input ren,
    input wen,
    input source, // 0 = take from left, 1 = take from right
    input [BYTE_ADDR_WIDTH-1:0] addr,
    input [DATA_WIDTH-1:0] left_i, right_i,
    output [DATA_WIDTH-1:0] left_o, right_o
);
    // Memory IO
    reg mem_wen;
    reg [BYTE_ADDR_WIDTH-1:0] mem_addr;
    reg [DATA_WIDTH-1:0] mem_din;
    wire [DATA_WIDTH-1:0] mem_dout;

    // Instantiate memories
    RAM_Array #(.DATA_WIDTH(DATA_WIDTH), .BYTE_ADDR_WIDTH(BYTE_ADDR_WIDTH)) memory (
        .clk(clk),
        .en(ren | mem_wen),
        .wen(mem_wen),
        .addr(mem_wen ? mem_addr : addr),
        .din(mem_din),
        .dout(mem_dout)
    );

    // assign mem_din = source ? right_i : left_i;
    assign right_o = ren ? mem_dout : left_i;
    assign left_o = ren ? mem_dout : right_i;

    always @(posedge clk) begin
        if (wen) begin
            mem_wen <= 1;
            mem_addr <= addr;
            mem_din <= source ? right_i : left_i;
        end else begin
            mem_wen <= 0;
        end
    end
endmodule
