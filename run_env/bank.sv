module bank #(
    parameter DATA_WIDTH = 32,
    parameter BYTE_ADDR_WIDTH = 8,
    parameter BANKS_ADDR_WIDTH = 2,
    localparam NUM_SB = 1 << BANKS_ADDR_WIDTH
) (
    input clk,
    input en,
    input wen,
    input [BYTE_ADDR_WIDTH+BANKS_ADDR_WIDTH-1:0] addr,
    input [DATA_WIDTH-1:0] din,
    output [DATA_WIDTH-1:0] dout
);
    wire [BYTE_ADDR_WIDTH-1:0] addr_select = addr[0 +: BYTE_ADDR_WIDTH];
    wire [BANKS_ADDR_WIDTH-1:0] bank_select = addr[BYTE_ADDR_WIDTH +: BANKS_ADDR_WIDTH];

    wire [DATA_WIDTH-1:0] dout_array [0:NUM_SB-1];
    assign dout = dout_array[bank_select];

    wire [NUM_SB-1:0] en_array = en << bank_select;

    generate
        genvar i;
        for (i = 0; i < NUM_SB; i = i + 1) begin: gen_sb
            RAM_Array #(.DATA_WIDTH(DATA_WIDTH), .BYTE_ADDR_WIDTH(BYTE_ADDR_WIDTH)) ram_array (
                .addr(addr_select),
                .din(din),
                .dout(dout_array[i]),
                .wen(wen),
                .en(en_array[i]),
                .clk(clk)
            );
        end
    endgenerate
endmodule
