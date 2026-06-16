#include <stdio.h>
#include <stdlib.h>

struct node {
    int data;
    struct node *next;
};

int main() {
    struct node *head = 0, *newnode, *temp;
    int choice = 1;

    while (choice) {
        newnode = (struct node*) malloc(sizeof(struct node));

        printf("Enter data: ");
        scanf("%d", &newnode->data);

        newnode->next = 0;

        if (head == 0) {
            head = temp = newnode;
        } 
        else {
            temp->next = newnode;
            temp = newnode;
        }

        printf("Do you want to continue (0/1)? ");
        scanf("%d", &choice);
    }

    // Print the linked list
    temp = head;
    while (temp != 0) {
        printf("%d ", temp->data);
        temp = temp->next;
    }

    return 0;
}
